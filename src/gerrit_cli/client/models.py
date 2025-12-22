"""Gerrit API Data Models"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Account(BaseModel):
    """Gerrit Account Info"""

    model_config = ConfigDict(populate_by_name=True)

    account_id: int = Field(alias="_account_id")
    name: str | None = None
    email: str | None = None
    username: str | None = None


class Change(BaseModel):
    """Change Basic Info"""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    project: str
    branch: str
    change_id: str
    subject: str
    status: str
    created: str
    updated: str
    insertions: int = 0
    deletions: int = 0
    number: int = Field(alias="_number")
    owner: Account | None = None
    current_revision: str | None = None
    more_changes: bool | None = Field(default=None, alias="_more_changes")

    @property
    def display_id(self) -> str:
        """Return display ID (number ID)"""
        return str(self.number)


class LabelInfo(BaseModel):
    """Label Info"""

    approved: Account | None = None
    rejected: Account | None = None
    recommended: Account | None = None
    disliked: Account | None = None
    value: int | None = None
    default_value: int | None = None
    values: dict[str, str] | None = None
    all: list[dict[str, Any]] | None = None


class MessageInfo(BaseModel):
    """Message Info"""

    id: str
    author: Account | None = None
    date: str
    message: str
    tag: str | None = None


class FileInfo(BaseModel):
    """File Info"""

    status: str | None = None
    binary: bool | None = None
    old_path: str | None = None
    lines_inserted: int | None = None
    lines_deleted: int | None = None
    size_delta: int | None = None
    size: int | None = None


class ChangeDetail(Change):
    """Change Detail"""

    messages: list[MessageInfo] | None = None
    labels: dict[str, LabelInfo] | None = None
    permitted_labels: dict[str, list[str]] | None = None
    reviewers: dict[str, list[Account]] | None = None
    revisions: dict[str, Any] | None = None


class CommentInfo(BaseModel):
    """Comment Info"""

    id: str | None = None
    patch_set: int | None = None
    path: str | None = None
    side: str | None = None
    line: int | None = None
    range: dict[str, Any] | None = None
    message: str
    updated: str | None = None
    author: Account | None = None
    unresolved: bool | None = None
    in_reply_to: str | None = None



class CommentRange(BaseModel):
    """Comment Range"""

    start_line: int
    start_character: int
    end_line: int
    end_character: int


class CommentInput(BaseModel):
    """Comment Input"""

    path: str | None = None
    line: int | None = None
    range: CommentRange | None = None
    message: str
    side: str = "REVISION"
    in_reply_to: str | None = None
    unresolved: bool | None = None


class ReviewInput(BaseModel):
    """Review Request Input"""

    message: str | None = None
    labels: dict[str, int] | None = None
    comments: dict[str, list[CommentInput]] | None = None
    tag: str | None = None
    notify: str | None = None
    drafts: str | None = None
    ready: bool | None = None
    work_in_progress: bool | None = None


class ReviewResult(BaseModel):
    """Review Response Result"""

    labels: dict[str, int] | None = None
    reviewers: dict[str, Any] | None = None
    ready: bool | None = None
