import pytest
from gerrit_cli.client.models import (
    Account,
    Change,
    ChangeDetail,
    CommentInfo,
    ReviewInput,
    CommentInput,
    MessageInfo,
    LabelInfo,
)


class TestChangeModel:
    """Test Change model serialization and field aliases"""

    def test_change_model_dump_basic(self, sample_change):
        """Test model_dump(mode='json') returns complete dict"""
        data = sample_change.model_dump(mode="json")

        assert isinstance(data, dict)
        assert data["id"] == "myproject~master~I1234567890"
        assert data["project"] == "myproject"
        assert data["subject"] == "Fix bug in parser"
        assert data["number"] == 12345
        assert data["insertions"] == 50
        assert data["deletions"] == 20

    def test_change_field_alias_number(self, sample_change_api_response):
        """Test _number alias maps to number field"""
        change = Change.model_validate(sample_change_api_response)

        assert change.number == 12345

        dumped = change.model_dump(mode="json")
        assert dumped["number"] == 12345
        assert "_number" not in dumped

    def test_change_field_alias_more_changes(self):
        """Test _more_changes alias maps to more_changes field"""
        api_response = {
            "id": "test~main~I123",
            "project": "test",
            "branch": "main",
            "change_id": "I123",
            "subject": "Test",
            "status": "NEW",
            "created": "2025-01-01 00:00:00.000000000",
            "updated": "2025-01-01 00:00:00.000000000",
            "_number": 999,
            "_more_changes": True,
        }

        change = Change.model_validate(api_response)
        assert change.more_changes is True

        dumped = change.model_dump(mode="json")
        assert dumped["more_changes"] is True
        assert "_more_changes" not in dumped

    def test_change_optional_owner_none(self):
        """Test owner=None serializes as null"""
        api_response = {
            "id": "test~main~I123",
            "project": "test",
            "branch": "main",
            "change_id": "I123",
            "subject": "Test",
            "status": "NEW",
            "created": "2025-01-01 00:00:00.000000000",
            "updated": "2025-01-01 00:00:00.000000000",
            "_number": 999,
        }

        change = Change.model_validate(api_response)
        assert change.owner is None

        dumped = change.model_dump(mode="json")
        assert dumped["owner"] is None

    def test_change_display_id_property(self, sample_change):
        """Test display_id property returns string"""
        assert sample_change.display_id == "12345"
        assert isinstance(sample_change.display_id, str)


class TestAccountModel:
    """Test Account model serialization and field aliases"""

    def test_account_field_alias_account_id(self):
        """Test _account_id alias maps to account_id field"""
        api_response = {
            "_account_id": 1000,
            "name": "Test User",
            "email": "test@example.com",
        }

        account = Account.model_validate(api_response)
        assert account.account_id == 1000

        dumped = account.model_dump(mode="json")
        assert dumped["account_id"] == 1000
        assert "_account_id" not in dumped

    def test_account_optional_fields(self):
        """Test email/username optional fields"""
        api_response = {"_account_id": 1000, "name": "User"}

        account = Account.model_validate(api_response)
        assert account.email is None
        assert account.username is None

        dumped = account.model_dump(mode="json")
        assert dumped["email"] is None
        assert dumped["username"] is None

    def test_account_model_validate(self, sample_account):
        """Test Account validates from dict correctly"""
        data = sample_account.model_dump()
        account2 = Account.model_validate(data)

        assert account2.account_id == 1000
        assert account2.name == "Test User"
        assert account2.email == "test@example.com"


class TestChangeDetailModel:
    """Test ChangeDetail model extends Change"""

    def test_change_detail_inherits_change(self, sample_change_detail):
        """Test ChangeDetail has all Change fields"""
        data = sample_change_detail.model_dump(mode="json")

        assert data["number"] == 12345
        assert data["project"] == "myproject"
        assert data["subject"] == "Fix bug in parser"
        assert data["owner"]["account_id"] == 1000

    def test_change_detail_extended_fields(self, sample_change_detail):
        """Test ChangeDetail has messages, labels, reviewers fields"""
        data = sample_change_detail.model_dump(mode="json")

        assert "messages" in data
        assert "labels" in data
        assert isinstance(data["messages"], list)
        assert isinstance(data["labels"], dict)

    def test_change_detail_nested_serialization(self, sample_change_detail):
        """Test nested MessageInfo/LabelInfo serialize correctly"""
        data = sample_change_detail.model_dump(mode="json")

        assert len(data["messages"]) == 1
        assert data["messages"][0]["id"] == "msg-001"
        assert data["messages"][0]["author"]["account_id"] == 1000

        assert "Code-Review" in data["labels"]
        assert data["labels"]["Code-Review"]["value"] == 2
        assert data["labels"]["Code-Review"]["approved"]["account_id"] == 1000


class TestCommentInfoModel:
    """Test CommentInfo model"""

    def test_comment_info_model_dump(self, sample_comment_info):
        """Test CommentInfo full serialization"""
        data = sample_comment_info.model_dump(mode="json")

        assert data["id"] == "comment-001"
        assert data["path"] == "src/main.py"
        assert data["line"] == 42
        assert data["message"] == "Consider using a helper function here"
        assert data["author"]["account_id"] == 1000

    def test_comment_info_optional_fields(self):
        """Test CommentInfo with minimal fields"""
        comment = CommentInfo(message="Simple comment")

        data = comment.model_dump(mode="json")
        assert data["message"] == "Simple comment"
        assert data["line"] is None
        assert data["author"] is None

    def test_comment_info_nested_range(self):
        """Test CommentInfo with range object"""
        from gerrit_cli.client.models import CommentRange

        comment_range = CommentRange(
            start_line=10, start_character=5, end_line=10, end_character=15
        )
        comment = CommentInfo(message="Range comment", range=comment_range.model_dump())

        data = comment.model_dump(mode="json")
        assert data["range"]["start_line"] == 10
        assert data["range"]["start_character"] == 5


class TestReviewInputModel:
    """Test ReviewInput model for API requests"""

    def test_review_input_exclude_none(self):
        """Test exclude_none=True excludes null fields"""
        review = ReviewInput(message="LGTM")

        data = review.model_dump(exclude_none=True, mode="json")
        assert "message" in data
        assert "labels" not in data
        assert "comments" not in data

    def test_review_input_nested_comments(self, sample_account):
        """Test ReviewInput with nested comments"""
        comment = CommentInput(path="src/main.py", line=10, message="Fix this")
        review = ReviewInput(comments={"src/main.py": [comment]})

        data = review.model_dump(mode="json")
        assert "src/main.py" in data["comments"]
        assert data["comments"]["src/main.py"][0]["line"] == 10
        assert data["comments"]["src/main.py"][0]["message"] == "Fix this"

    def test_review_input_with_labels(self):
        """Test ReviewInput with labels"""
        review = ReviewInput(labels={"Code-Review": 2, "Verified": 1})

        data = review.model_dump(exclude_none=True, mode="json")
        assert data["labels"]["Code-Review"] == 2
        assert data["labels"]["Verified"] == 1


class TestFieldAliasMapping:
    """Test comprehensive field alias mapping"""

    def test_all_gerrit_aliases_mapped_correctly(self):
        """Test all Gerrit _field aliases map to standard names"""
        api_response = {
            "id": "test~main~I123",
            "project": "test",
            "branch": "main",
            "change_id": "I123",
            "subject": "Test",
            "status": "NEW",
            "created": "2025-01-01 00:00:00.000000000",
            "updated": "2025-01-01 00:00:00.000000000",
            "_number": 12345,
            "_more_changes": False,
            "owner": {"_account_id": 1000, "name": "User"},
        }

        change = Change.model_validate(api_response)
        dumped = change.model_dump(mode="json")

        assert dumped["number"] == 12345
        assert dumped["more_changes"] is False
        assert dumped["owner"]["account_id"] == 1000

        assert "_number" not in dumped
        assert "_more_changes" not in dumped
        assert "_account_id" not in dumped["owner"]

    def test_model_round_trip_preserves_data(self, sample_change_api_response):
        """Test model -> JSON -> model preserves all data"""
        change1 = Change.model_validate(sample_change_api_response)

        dumped = change1.model_dump(mode="json")

        change2 = Change.model_validate(dumped)

        assert change1.number == change2.number
        assert change1.subject == change2.subject
        assert change1.owner.account_id == change2.owner.account_id
