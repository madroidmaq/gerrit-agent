import json
import pytest
import respx
from httpx import Response
from gerrit_cli.client.api import GerritClient
from gerrit_cli.client.models import Change, ChangeDetail, CommentInfo
from gerrit_cli.utils.exceptions import ApiError


class TestGerritClientResponseParsing:
    """Test GerritClient response parsing"""

    @respx.mock
    def test_parse_response_strips_xssi_prefix(self, sample_change_api_response):
        """Test XSSI prefix )]}' is stripped before parsing"""
        respx.get("https://gerrit.example.com/a/changes/").mock(
            return_value=Response(
                200, text=")]}'\n" + json.dumps([sample_change_api_response])
            )
        )

        with GerritClient("https://gerrit.example.com", "user", "pass") as client:
            changes = client.list_changes()

        assert len(changes) == 1
        assert changes[0].number == 12345

    @respx.mock
    def test_parse_response_empty_body(self):
        """Test empty response body returns empty dict/list"""
        respx.get("https://gerrit.example.com/a/changes/").mock(
            return_value=Response(200, text=")]}'\n[]")
        )

        with GerritClient("https://gerrit.example.com", "user", "pass") as client:
            changes = client.list_changes()

        assert changes == []

    @respx.mock
    def test_parse_response_invalid_json_raises_error(self):
        """Test invalid JSON raises ApiError"""
        respx.get("https://gerrit.example.com/a/changes/").mock(
            return_value=Response(200, text=")]}'\ninvalid json")
        )

        with pytest.raises(ApiError, match="JSON parse failed"):
            with GerritClient("https://gerrit.example.com", "user", "pass") as client:
                client.list_changes()


class TestGerritClientListChanges:
    """Test list_changes() method"""

    @respx.mock
    def test_list_changes_returns_change_models(self, sample_change_api_response):
        """Test list_changes returns list of Change models"""
        respx.get("https://gerrit.example.com/a/changes/").mock(
            return_value=Response(
                200, text=")]}'\n" + json.dumps([sample_change_api_response])
            )
        )

        with GerritClient("https://gerrit.example.com", "user", "pass") as client:
            changes = client.list_changes()

        assert isinstance(changes, list)
        assert len(changes) == 1
        assert isinstance(changes[0], Change)
        assert changes[0].number == 12345
        assert changes[0].subject == "Fix bug in parser"

    @respx.mock
    def test_list_changes_empty_result(self):
        """Test list_changes with empty result"""
        respx.get("https://gerrit.example.com/a/changes/").mock(
            return_value=Response(200, text=")]}'\n[]")
        )

        with GerritClient("https://gerrit.example.com", "user", "pass") as client:
            changes = client.list_changes()

        assert changes == []

    @respx.mock
    def test_list_changes_with_options(self, sample_change_api_response):
        """Test list_changes with options parameter"""
        route = respx.get("https://gerrit.example.com/a/changes/").mock(
            return_value=Response(
                200, text=")]}'\n" + json.dumps([sample_change_api_response])
            )
        )

        with GerritClient("https://gerrit.example.com", "user", "pass") as client:
            changes = client.list_changes(options=["LABELS", "CURRENT_REVISION"])

        assert route.called
        request_url = str(route.calls.last.request.url)
        assert "o=LABELS" in request_url
        assert "o=CURRENT_REVISION" in request_url


class TestGerritClientGetChangeDetail:
    """Test get_change_detail() method"""

    @respx.mock
    def test_get_change_detail_returns_change_detail_model(self, sample_change_api_response):
        """Test get_change_detail returns ChangeDetail model"""
        change_detail_response = {
            **sample_change_api_response,
            "messages": [],
            "labels": {},
        }

        respx.get("https://gerrit.example.com/a/changes/12345").mock(
            return_value=Response(200, text=")]}'\n" + json.dumps(change_detail_response))
        )

        with GerritClient("https://gerrit.example.com", "user", "pass") as client:
            change = client.get_change_detail("12345")

        assert isinstance(change, ChangeDetail)
        assert change.number == 12345
        assert hasattr(change, "messages")
        assert hasattr(change, "labels")

    @respx.mock
    def test_get_change_detail_validates_nested_objects(self, sample_change_api_response):
        """Test nested objects are validated correctly"""
        change_detail_response = {
            **sample_change_api_response,
            "messages": [
                {
                    "id": "msg-1",
                    "author": {"_account_id": 1000, "name": "Reviewer"},
                    "date": "2025-01-01 10:00:00.000000000",
                    "message": "LGTM",
                }
            ],
            "labels": {
                "Code-Review": {
                    "value": 2,
                    "approved": {"_account_id": 1000, "name": "Approver"},
                }
            },
        }

        respx.get("https://gerrit.example.com/a/changes/12345").mock(
            return_value=Response(200, text=")]}'\n" + json.dumps(change_detail_response))
        )

        with GerritClient("https://gerrit.example.com", "user", "pass") as client:
            change = client.get_change_detail("12345")

        assert len(change.messages) == 1
        assert change.messages[0].author.account_id == 1000
        assert change.labels["Code-Review"].value == 2
        assert change.labels["Code-Review"].approved.account_id == 1000


class TestGerritClientGetChangeComments:
    """Test get_change_comments() method"""

    @respx.mock
    def test_get_change_comments_returns_dict(self):
        """Test get_change_comments returns dict of lists"""
        comments_response = {
            "src/main.py": [
                {
                    "id": "comment-1",
                    "line": 42,
                    "message": "Fix this",
                    "author": {"_account_id": 1000, "name": "Reviewer"},
                    "updated": "2025-01-01 10:00:00.000000000",
                }
            ]
        }

        respx.get("https://gerrit.example.com/a/changes/12345/comments").mock(
            return_value=Response(200, text=")]}'\n" + json.dumps(comments_response))
        )

        with GerritClient("https://gerrit.example.com", "user", "pass") as client:
            comments = client.get_change_comments("12345")

        assert isinstance(comments, dict)
        assert "src/main.py" in comments
        assert isinstance(comments["src/main.py"], list)
        assert isinstance(comments["src/main.py"][0], CommentInfo)
        assert comments["src/main.py"][0].line == 42

    @respx.mock
    def test_get_change_comments_empty(self):
        """Test get_change_comments with no comments"""
        respx.get("https://gerrit.example.com/a/changes/12345/comments").mock(
            return_value=Response(200, text=")]}'\n{}")
        )

        with GerritClient("https://gerrit.example.com", "user", "pass") as client:
            comments = client.get_change_comments("12345")

        assert comments == {}
