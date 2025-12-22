import json
import pytest
import respx
from httpx import Response
from gerrit_cli.cli import main as cli


class TestListCommandJsonOutput:
    """Test 'gerrit list --format json' command"""

    @respx.mock
    def test_list_command_json_empty(self, runner, gerrit_env):
        """Test list command with JSON format returns empty array"""
        respx.get("https://gerrit.example.com/a/changes/").mock(
            return_value=Response(200, text=")]}'\n[]")
        )

        result = runner.invoke(cli, ["list", "--format", "json"], env=gerrit_env)

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == []

    @respx.mock
    def test_list_command_json_single_change(self, runner, gerrit_env, sample_change_api_response):
        """Test list command returns single change in JSON array"""
        respx.get("https://gerrit.example.com/a/changes/").mock(
            return_value=Response(
                200, text=")]}'\n" + json.dumps([sample_change_api_response])
            )
        )

        result = runner.invoke(cli, ["list", "--format", "json"], env=gerrit_env)

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["number"] == 12345
        assert data[0]["subject"] == "Fix bug in parser"

    @respx.mock
    def test_list_command_json_multiple_changes(self, runner, gerrit_env, sample_change_api_response):
        """Test list command returns multiple changes"""
        change2 = {**sample_change_api_response, "_number": 12346, "subject": "Second change"}
        change3 = {**sample_change_api_response, "_number": 12347, "subject": "Third change"}

        respx.get("https://gerrit.example.com/a/changes/").mock(
            return_value=Response(
                200,
                text=")]}'\n" + json.dumps([sample_change_api_response, change2, change3]),
            )
        )

        result = runner.invoke(cli, ["list", "--format", "json"], env=gerrit_env)

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 3
        assert data[0]["number"] == 12345
        assert data[1]["number"] == 12346
        assert data[2]["number"] == 12347

    @respx.mock
    def test_list_command_json_with_query(self, runner, gerrit_env, sample_change_api_response):
        """Test list command with query parameter"""
        route = respx.get("https://gerrit.example.com/a/changes/").mock(
            return_value=Response(
                200, text=")]}'\n" + json.dumps([sample_change_api_response])
            )
        )

        result = runner.invoke(
            cli, ["list", "--query", "status:merged", "--format", "json"], env=gerrit_env
        )

        assert result.exit_code == 0
        assert route.called
        assert "status%3Amerged" in str(route.calls.last.request.url)

    @respx.mock
    def test_list_command_json_with_owner(self, runner, gerrit_env, sample_change_api_response):
        """Test list command with owner parameter"""
        route = respx.get("https://gerrit.example.com/a/changes/").mock(
            return_value=Response(
                200, text=")]}'\n" + json.dumps([sample_change_api_response])
            )
        )

        result = runner.invoke(
            cli, ["list", "--owner", "me", "--format", "json"], env=gerrit_env
        )

        assert result.exit_code == 0
        assert route.called
        assert "owner%3Atest_user" in str(route.calls.last.request.url)

    @respx.mock
    def test_list_command_json_strips_xssi_prefix(self, runner, gerrit_env, sample_change_api_response):
        """Test XSSI prefix is properly stripped"""
        respx.get("https://gerrit.example.com/a/changes/").mock(
            return_value=Response(
                200, text=")]}'\n" + json.dumps([sample_change_api_response])
            )
        )

        result = runner.invoke(cli, ["list", "--format", "json"], env=gerrit_env)

        assert result.exit_code == 0
        assert not result.output.startswith(")]}'\n")

        data = json.loads(result.output)
        assert isinstance(data, list)


class TestViewCommandJsonOutput:
    """Test 'gerrit show --format json' command"""

    @respx.mock
    def test_view_command_json_basic(self, runner, gerrit_env, sample_change_api_response):
        """Test view command basic JSON output"""
        change_detail = {
            **sample_change_api_response,
            "messages": [],
            "labels": {},
        }

        respx.get("https://gerrit.example.com/a/changes/12345").mock(
            return_value=Response(200, text=")]}'\n" + json.dumps(change_detail))
        )
        respx.get("https://gerrit.example.com/a/changes/12345/revisions/current/files/").mock(
            return_value=Response(200, text=")]}'\n{}")
        )
        respx.get("https://gerrit.example.com/a/changes/12345/comments").mock(
            return_value=Response(200, text=")]}'\n{}")
        )

        result = runner.invoke(cli, ["show", "12345", "--format", "json"], env=gerrit_env)

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "change" in data
        assert data["change"]["number"] == 12345

    @respx.mock
    def test_view_command_json_structure(self, runner, gerrit_env, sample_change_api_response):
        """Test view command JSON structure contains expected keys"""
        change_detail = {
            **sample_change_api_response,
            "messages": [],
            "labels": {},
        }

        respx.get("https://gerrit.example.com/a/changes/12345").mock(
            return_value=Response(200, text=")]}'\n" + json.dumps(change_detail))
        )
        respx.get("https://gerrit.example.com/a/changes/12345/revisions/current/files/").mock(
            return_value=Response(200, text=")]}'\n{}")
        )

        result = runner.invoke(
            cli, ["show", "12345", "--format", "json", "--parts", "m,f"], env=gerrit_env
        )

        assert result.exit_code == 0
        data = json.loads(result.output)

        assert "change" in data

    @respx.mock
    def test_view_command_json_only_metadata(self, runner, gerrit_env, sample_change_api_response):
        """Test view command with only metadata part"""
        change_detail = {
            **sample_change_api_response,
            "messages": [],
            "labels": {},
        }

        route_detail = respx.get("https://gerrit.example.com/a/changes/12345").mock(
            return_value=Response(200, text=")]}'\n" + json.dumps(change_detail))
        )

        result = runner.invoke(
            cli, ["show", "12345", "--format", "json", "--parts", "m"], env=gerrit_env
        )

        assert result.exit_code == 0
        assert route_detail.called

        data = json.loads(result.output)
        assert "change" in data

    @respx.mock
    def test_view_command_json_nested_integrity(self, runner, gerrit_env, sample_change_api_response):
        """Test nested data integrity in JSON output"""
        change_detail = {
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
            return_value=Response(200, text=")]}'\n" + json.dumps(change_detail))
        )
        respx.get("https://gerrit.example.com/a/changes/12345/revisions/current/files/").mock(
            return_value=Response(200, text=")]}'\n{}")
        )
        respx.get("https://gerrit.example.com/a/changes/12345/comments").mock(
            return_value=Response(200, text=")]}'\n{}")
        )

        result = runner.invoke(cli, ["show", "12345", "--format", "json"], env=gerrit_env)

        assert result.exit_code == 0
        data = json.loads(result.output)

        assert data["change"]["messages"][0]["author"]["account_id"] == 1000
        assert data["change"]["labels"]["Code-Review"]["approved"]["account_id"] == 1000
        assert data["change"]["owner"]["account_id"] == 1000

    @respx.mock
    def test_view_command_json_with_comments(self, runner, gerrit_env, sample_change_api_response):
        """Test view command JSON output with comments"""
        change_detail = {
            **sample_change_api_response,
            "messages": [],
            "labels": {},
        }

        comments_response = {
            "src/main.py": [
                {
                    "id": "comment-1",
                    "patch_set": 1,
                    "line": 42,
                    "message": "This needs improvement",
                    "updated": "2025-01-01 10:00:00.000000000",
                    "author": {"_account_id": 1000, "name": "Reviewer"},
                    "unresolved": True,
                }
            ]
        }

        respx.get("https://gerrit.example.com/a/changes/12345").mock(
            return_value=Response(200, text=")]}'\n" + json.dumps(change_detail))
        )
        respx.get("https://gerrit.example.com/a/changes/12345/revisions/current/files/").mock(
            return_value=Response(200, text=")]}'\n{}")
        )
        respx.get("https://gerrit.example.com/a/changes/12345/comments").mock(
            return_value=Response(200, text=")]}'\n" + json.dumps(comments_response))
        )

        result = runner.invoke(cli, ["show", "12345", "--format", "json"], env=gerrit_env)

        assert result.exit_code == 0
        data = json.loads(result.output)

        # Verify comments are properly serialized
        assert "comments" in data
        assert "src/main.py" in data["comments"]
        assert len(data["comments"]["src/main.py"]) == 1
        assert data["comments"]["src/main.py"][0]["id"] == "comment-1"
        assert data["comments"]["src/main.py"][0]["line"] == 42
        assert data["comments"]["src/main.py"][0]["message"] == "This needs improvement"
        assert data["comments"]["src/main.py"][0]["unresolved"] is True

    @respx.mock
    def test_list_command_json_with_more_changes(self, runner, gerrit_env, sample_change_api_response):
        """Test list command with _more_changes flag"""
        change_with_more = {**sample_change_api_response, "_more_changes": True}

        respx.get("https://gerrit.example.com/a/changes/").mock(
            return_value=Response(200, text=")]}'\n" + json.dumps([change_with_more]))
        )

        result = runner.invoke(cli, ["list", "--format", "json"], env=gerrit_env)

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 1
        assert data[0]["more_changes"] is True

    @respx.mock
    def test_list_command_json_with_limit(self, runner, gerrit_env, sample_change_api_response):
        """Test list command with custom limit parameter"""
        route = respx.get("https://gerrit.example.com/a/changes/").mock(
            return_value=Response(200, text=")]}'\n" + json.dumps([sample_change_api_response]))
        )

        result = runner.invoke(
            cli, ["list", "--limit", "50", "--format", "json"], env=gerrit_env
        )

        assert result.exit_code == 0
        assert route.called
        assert "n=50" in str(route.calls.last.request.url)

        data = json.loads(result.output)
        assert len(data) == 1
