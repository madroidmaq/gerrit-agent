import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    """CliRunner for CLI testing"""
    return CliRunner()


@pytest.fixture
def gerrit_env():
    """Standard environment variables for tests"""
    return {
        "GERRIT_URL": "https://gerrit.example.com",
        "GERRIT_USERNAME": "test_user",
        "GERRIT_PASSWORD": "test_password",
    }


@pytest.fixture
def sample_account():
    """Sample Account model"""
    from gerrit_cli.client.models import Account

    return Account(
        account_id=1000, name="Test User", email="test@example.com", username="testuser"
    )


@pytest.fixture
def sample_change(sample_account):
    """Sample Change model with all fields"""
    from gerrit_cli.client.models import Change

    return Change(
        id="myproject~master~I1234567890",
        project="myproject",
        branch="master",
        change_id="I1234567890",
        subject="Fix bug in parser",
        status="NEW",
        created="2025-01-01 10:00:00.000000000",
        updated="2025-01-10 15:30:00.000000000",
        insertions=50,
        deletions=20,
        number=12345,
        owner=sample_account,
        current_revision="abcdef1234567890",
    )


@pytest.fixture
def sample_change_api_response():
    """Raw API response dict for a change (with Gerrit field aliases)"""
    return {
        "id": "myproject~master~I1234567890",
        "project": "myproject",
        "branch": "master",
        "change_id": "I1234567890",
        "subject": "Fix bug in parser",
        "status": "NEW",
        "created": "2025-01-01 10:00:00.000000000",
        "updated": "2025-01-10 15:30:00.000000000",
        "insertions": 50,
        "deletions": 20,
        "_number": 12345,
        "owner": {
            "_account_id": 1000,
            "name": "Test User",
            "email": "test@example.com",
        },
        "current_revision": "abcdef1234567890",
    }


@pytest.fixture
def sample_message_info(sample_account):
    """Sample MessageInfo"""
    from gerrit_cli.client.models import MessageInfo

    return MessageInfo(
        id="msg-001",
        author=sample_account,
        date="2025-01-02 12:00:00.000000000",
        message="Patch Set 1: Code-Review+2\n\nLGTM!",
    )


@pytest.fixture
def sample_label_info(sample_account):
    """Sample LabelInfo"""
    from gerrit_cli.client.models import LabelInfo

    return LabelInfo(
        value=2,
        approved=sample_account,
    )


@pytest.fixture
def sample_change_detail(sample_change, sample_message_info, sample_label_info):
    """Sample ChangeDetail with messages and labels"""
    from gerrit_cli.client.models import ChangeDetail

    return ChangeDetail(
        **sample_change.model_dump(),
        messages=[sample_message_info],
        labels={"Code-Review": sample_label_info},
    )


@pytest.fixture
def sample_comment_info(sample_account):
    """Sample CommentInfo"""
    from gerrit_cli.client.models import CommentInfo

    return CommentInfo(
        id="comment-001",
        patch_set=1,
        path="src/main.py",
        line=42,
        message="Consider using a helper function here",
        author=sample_account,
        updated="2025-01-03 09:00:00.000000000",
    )


@pytest.fixture
def minimal_change():
    """Minimal Change with only required fields"""
    from gerrit_cli.client.models import Change

    return Change(
        id="project~branch~I123",
        project="test-project",
        branch="main",
        change_id="I123",
        subject="Minimal change",
        status="NEW",
        created="2025-01-01 00:00:00.000000000",
        updated="2025-01-01 00:00:00.000000000",
        number=100,
    )
