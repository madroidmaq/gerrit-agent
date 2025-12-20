import pytest
import respx
from httpx import Response
from click.testing import CliRunner
from gerrit_cli.cli import main as cli
from gerrit_cli.client.models import ReviewInput

@pytest.fixture
def runner():
    return CliRunner()

@respx.mock
def test_review_inline_comment(runner):
    # Mock API
    route = respx.post("https://gerrit.example.com/a/changes/12345/revisions/current/review").mock(
        return_value=Response(200, json={"labels": {"Code-Review": 2}})
    )

    result = runner.invoke(
        cli,
        [
            "review",
            "12345",
            "--inline-comment",
            "src/main.py#10",
            "Fix typo",
            "--inline-comment",
            "src/utils.py#20",
            "Refactor this",
            "--inline-comment",
            "src/range.py#10-20",
            "Multi-line comment",
            "--inline-comment",
            "src/utils.py#L12C13-L12C19",
            "Char range",
        ],
        env={
            "GERRIT_URL": "https://gerrit.example.com",
            "GERRIT_USERNAME": "user",
            "GERRIT_PASSWORD": "password",
        },
    )

    assert result.exit_code == 0
    assert "Review sent to Change 12345" in result.output

    # Verify request payload
    assert route.called
    request_data = ReviewInput.model_validate_json(route.calls.last.request.content)
    
    assert request_data.comments is not None
    assert "src/main.py" in request_data.comments
    assert "src/utils.py" in request_data.comments
    assert "src/range.py" in request_data.comments
    
    assert request_data.comments["src/main.py"][0].line == 10
    assert request_data.comments["src/main.py"][0].message == "Fix typo"
    
    assert request_data.comments["src/utils.py"][0].line == 20
    assert request_data.comments["src/utils.py"][0].message == "Refactor this"

    range_comment = request_data.comments["src/range.py"][0]
    assert range_comment.line == 20
    assert range_comment.message == "Multi-line comment"
    assert range_comment.range is not None
    assert range_comment.range.start_line == 10
    assert range_comment.range.start_character == 0
    assert range_comment.range.end_line == 20
    assert range_comment.range.end_character == 10000

    char_comment = request_data.comments["src/utils.py"][1]
    assert char_comment.line == 12
    assert char_comment.message == "Char range"
    assert char_comment.range is not None
    assert char_comment.range.start_line == 12
    assert char_comment.range.start_character == 13
    assert char_comment.range.end_line == 12
    assert char_comment.range.end_character == 19

@respx.mock
def test_review_mixed_inline_and_labels(runner):
    # Mock API
    route = respx.post("https://gerrit.example.com/a/changes/12345/revisions/current/review").mock(
        return_value=Response(200, json={"labels": {"Code-Review": 2}})
    )

    result = runner.invoke(
        cli,
        [
            "review",
            "12345",
            "--code-review",
            "+2",
            "--inline-comment",
            "src/main.py#10",
            "Nice fix",
        ],
        env={
            "GERRIT_URL": "https://gerrit.example.com",
            "GERRIT_USERNAME": "user",
            "GERRIT_PASSWORD": "password",
        },
    )

    assert result.exit_code == 0
    assert "Review sent to Change 12345" in result.output
    
    # Verify request payload
    assert route.called
    request_data = ReviewInput.model_validate_json(route.calls.last.request.content)
    
    assert request_data.labels is not None
    assert request_data.labels["Code-Review"] == 2
    
    assert request_data.comments is not None
    assert "src/main.py" in request_data.comments
    assert request_data.comments["src/main.py"][0].message == "Nice fix"
