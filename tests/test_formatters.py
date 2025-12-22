import json
import pytest
from gerrit_cli.formatters.json import JsonFormatter
from gerrit_cli.formatters import get_formatter
from gerrit_cli.client.models import Change, ChangeDetail, Account, MessageInfo, LabelInfo


class TestJsonFormatterBasicFunctionality:
    """Test basic functionality of JsonFormatter"""

    def test_json_format_empty_changes_list(self):
        """Test formatting empty changes list returns empty JSON array"""
        formatter = JsonFormatter()
        result = formatter.format_changes([])

        assert isinstance(result, str)
        data = json.loads(result)
        assert data == []

    def test_json_format_single_change(self, sample_change):
        """Test formatting single Change object with all fields"""
        formatter = JsonFormatter()
        result = formatter.format_changes([sample_change])

        assert isinstance(result, str)
        data = json.loads(result)

        assert isinstance(data, list)
        assert len(data) == 1

        item = data[0]
        assert item["id"] == "myproject~master~I1234567890"
        assert item["project"] == "myproject"
        assert item["branch"] == "master"
        assert item["subject"] == "Fix bug in parser"
        assert item["status"] == "NEW"
        assert item["number"] == 12345
        assert item["insertions"] == 50
        assert item["deletions"] == 20
        assert item["owner"]["account_id"] == 1000
        assert item["owner"]["name"] == "Test User"

    def test_json_format_multiple_changes(self, sample_change, sample_account):
        """Test formatting multiple Change objects preserves order"""
        change2 = Change(
            id="project2~main~I999",
            project="project2",
            branch="main",
            change_id="I999",
            subject="Second change",
            status="MERGED",
            created="2025-01-02 10:00:00.000000000",
            updated="2025-01-02 11:00:00.000000000",
            number=12346,
            owner=sample_account,
        )

        formatter = JsonFormatter()
        result = formatter.format_changes([sample_change, change2])

        data = json.loads(result)
        assert len(data) == 2
        assert data[0]["number"] == 12345
        assert data[1]["number"] == 12346
        assert data[1]["status"] == "MERGED"

    def test_json_format_change_detail_basic(self, sample_change_detail):
        """Test formatting ChangeDetail object with extended fields"""
        formatter = JsonFormatter()
        result = formatter.format_change_detail(sample_change_detail)

        data = json.loads(result)

        assert data["number"] == 12345
        assert "messages" in data
        assert "labels" in data
        assert isinstance(data["messages"], list)
        assert isinstance(data["labels"], dict)


class TestJsonFormatterNestedObjects:
    """Test nested object serialization"""

    def test_json_format_change_with_owner(self, sample_change):
        """Test nested Account object serialization"""
        formatter = JsonFormatter()
        result = formatter.format_changes([sample_change])

        data = json.loads(result)
        owner = data[0]["owner"]

        assert owner is not None
        assert owner["account_id"] == 1000
        assert owner["name"] == "Test User"
        assert owner["email"] == "test@example.com"
        assert owner["username"] == "testuser"

    def test_json_format_change_detail_with_messages(self, sample_change_detail):
        """Test messages array serialization"""
        formatter = JsonFormatter()
        result = formatter.format_change_detail(sample_change_detail)

        data = json.loads(result)
        messages = data["messages"]

        assert len(messages) == 1
        assert messages[0]["id"] == "msg-001"
        assert messages[0]["message"] == "Patch Set 1: Code-Review+2\n\nLGTM!"
        assert messages[0]["author"]["account_id"] == 1000

    def test_json_format_change_detail_with_labels(self, sample_change_detail):
        """Test labels dict serialization"""
        formatter = JsonFormatter()
        result = formatter.format_change_detail(sample_change_detail)

        data = json.loads(result)
        labels = data["labels"]

        assert "Code-Review" in labels
        assert labels["Code-Review"]["value"] == 2
        assert labels["Code-Review"]["approved"]["account_id"] == 1000

    def test_json_format_nested_structure_integrity(self, sample_change_detail):
        """Test multi-level nested objects maintain integrity"""
        formatter = JsonFormatter()
        result = formatter.format_change_detail(sample_change_detail)

        data = json.loads(result)

        assert data["messages"][0]["author"]["name"] == "Test User"
        assert data["labels"]["Code-Review"]["approved"]["name"] == "Test User"
        assert data["owner"]["account_id"] == 1000


class TestJsonFormatterEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_json_format_change_with_none_owner(self, minimal_change):
        """Test Change with owner=None outputs null"""
        formatter = JsonFormatter()
        result = formatter.format_changes([minimal_change])

        data = json.loads(result)
        assert data[0]["owner"] is None

    def test_json_format_minimal_change(self, minimal_change):
        """Test Change with only required fields"""
        formatter = JsonFormatter()
        result = formatter.format_changes([minimal_change])

        data = json.loads(result)
        item = data[0]

        assert item["number"] == 100
        assert item["subject"] == "Minimal change"
        assert item["insertions"] == 0
        assert item["deletions"] == 0
        assert item["owner"] is None

    def test_json_format_empty_labels(self, sample_change):
        """Test ChangeDetail with empty labels dict"""
        change_detail = ChangeDetail(
            **sample_change.model_dump(), messages=[], labels={}
        )

        formatter = JsonFormatter()
        result = formatter.format_change_detail(change_detail)

        data = json.loads(result)
        assert data["labels"] == {}


class TestJsonFormatterCharacterEncoding:
    """Test character encoding and special characters"""

    def test_json_format_utf8_characters(self, sample_account):
        """Test UTF-8 characters (Chinese, emoji) are preserved"""
        change = Change(
            id="test~main~I456",
            project="test-project",
            branch="main",
            change_id="I456",
            subject="修复Bug 🐛 in system",
            status="NEW",
            created="2025-01-01 10:00:00.000000000",
            updated="2025-01-01 11:00:00.000000000",
            number=999,
            owner=sample_account,
        )

        formatter = JsonFormatter()
        result = formatter.format_changes([change])

        assert "修复Bug 🐛" in result
        assert "\\u" not in result

        data = json.loads(result)
        assert data[0]["subject"] == "修复Bug 🐛 in system"

    def test_json_format_special_characters(self, sample_account):
        """Test JSON special characters are properly escaped"""
        change = Change(
            id="test~main~I789",
            project="test-project",
            branch="main",
            change_id="I789",
            subject='Test "quotes" and\nnewlines\ttabs',
            status="NEW",
            created="2025-01-01 10:00:00.000000000",
            updated="2025-01-01 11:00:00.000000000",
            number=888,
            owner=sample_account,
        )

        formatter = JsonFormatter()
        result = formatter.format_changes([change])

        data = json.loads(result)
        assert data[0]["subject"] == 'Test "quotes" and\nnewlines\ttabs'


class TestJsonFormatterFormat:
    """Test JSON output format"""

    def test_json_indentation_format(self, sample_change):
        """Test indent=2 produces proper formatting"""
        formatter = JsonFormatter()
        result = formatter.format_changes([sample_change])

        lines = result.split("\n")
        assert len(lines) > 1

        assert any("  " in line for line in lines)

    def test_json_output_is_valid(self, sample_change):
        """Test output is always valid parseable JSON"""
        formatter = JsonFormatter()
        result = formatter.format_changes([sample_change])

        try:
            data = json.loads(result)
            assert isinstance(data, list)
        except json.JSONDecodeError:
            pytest.fail("Output is not valid JSON")


class TestFormatterFactory:
    """Test formatter factory function"""

    def test_get_formatter_factory_json(self):
        """Test get_formatter('json') returns JsonFormatter"""
        formatter = get_formatter("json")
        assert isinstance(formatter, JsonFormatter)

    def test_get_formatter_factory_invalid(self):
        """Test get_formatter with invalid type raises ValueError"""
        with pytest.raises(ValueError, match="Unsupported format type"):
            get_formatter("invalid_format")


class TestFormatterParameters:
    """Test formatter parameter handling"""

    def test_json_format_has_more_flag_ignored(self, sample_change):
        """Test has_more parameter doesn't affect JSON output"""
        formatter = JsonFormatter()
        result1 = formatter.format_changes([sample_change], has_more=False)
        result2 = formatter.format_changes([sample_change], has_more=True)

        assert result1 == result2

    def test_json_format_show_comments_flag_ignored(self, sample_change_detail):
        """Test show_comments parameter doesn't affect JSON output"""
        formatter = JsonFormatter()
        result1 = formatter.format_change_detail(sample_change_detail, show_comments=False)
        result2 = formatter.format_change_detail(sample_change_detail, show_comments=True)

        assert result1 == result2


class TestJsonFormatterAdvancedScenarios:
    """Test advanced scenarios and edge cases"""

    def test_json_format_different_statuses(self, sample_account):
        """Test formatting changes with different statuses"""
        statuses = ["NEW", "MERGED", "ABANDONED", "SUBMITTED"]
        changes = []

        for i, status in enumerate(statuses):
            change = Change(
                id=f"project~main~I{i}",
                project="test",
                branch="main",
                change_id=f"I{i}",
                subject=f"Change {i}",
                status=status,
                created="2025-01-01 00:00:00.000000000",
                updated="2025-01-01 00:00:00.000000000",
                number=1000 + i,
            )
            changes.append(change)

        formatter = JsonFormatter()
        result = formatter.format_changes(changes)

        data = json.loads(result)
        assert len(data) == 4
        for i, item in enumerate(data):
            assert item["status"] == statuses[i]

    def test_json_format_large_numbers(self, sample_account):
        """Test formatting changes with very large insertions/deletions"""
        change = Change(
            id="test~main~I999",
            project="test",
            branch="main",
            change_id="I999",
            subject="Large change",
            status="NEW",
            created="2025-01-01 00:00:00.000000000",
            updated="2025-01-01 00:00:00.000000000",
            number=99999,
            insertions=999999,
            deletions=888888,
            owner=sample_account,
        )

        formatter = JsonFormatter()
        result = formatter.format_changes([change])

        data = json.loads(result)
        assert data[0]["number"] == 99999
        assert data[0]["insertions"] == 999999
        assert data[0]["deletions"] == 888888

    def test_json_format_timestamp_format(self, sample_change):
        """Test timestamp fields are preserved correctly in Gerrit format"""
        formatter = JsonFormatter()
        result = formatter.format_changes([sample_change])

        data = json.loads(result)
        # Gerrit timestamps: "YYYY-MM-DD HH:MM:SS.000000000"
        assert data[0]["created"] == "2025-01-01 10:00:00.000000000"
        assert data[0]["updated"] == "2025-01-10 15:30:00.000000000"
        assert "." in data[0]["created"]
        assert len(data[0]["created"].split(".")[-1]) == 9  # 9 decimal places

    def test_json_format_none_current_revision(self, sample_account):
        """Test Change with None current_revision"""
        change = Change(
            id="test~main~I123",
            project="test",
            branch="main",
            change_id="I123",
            subject="Test",
            status="NEW",
            created="2025-01-01 00:00:00.000000000",
            updated="2025-01-01 00:00:00.000000000",
            number=100,
            owner=sample_account,
            current_revision=None,
        )

        formatter = JsonFormatter()
        result = formatter.format_changes([change])

        data = json.loads(result)
        assert data[0]["current_revision"] is None

    def test_json_format_zero_insertions_deletions(self, sample_account):
        """Test Change with zero insertions and deletions"""
        change = Change(
            id="test~main~I456",
            project="test",
            branch="main",
            change_id="I456",
            subject="No code changes",
            status="NEW",
            created="2025-01-01 00:00:00.000000000",
            updated="2025-01-01 00:00:00.000000000",
            number=200,
            insertions=0,
            deletions=0,
            owner=sample_account,
        )

        formatter = JsonFormatter()
        result = formatter.format_changes([change])

        data = json.loads(result)
        assert data[0]["insertions"] == 0
        assert data[0]["deletions"] == 0
