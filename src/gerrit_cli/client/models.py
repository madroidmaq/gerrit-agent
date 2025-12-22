"""Gerrit API Data Models"""

from typing import Any, List, Optional, Union, Dict

from pydantic import BaseModel, ConfigDict, Field


class Account(BaseModel):
    """Gerrit Account Info"""

    model_config = ConfigDict(populate_by_name=True)

    account_id: int = Field(alias="_account_id")
    name: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None


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
    owner: Optional[Account] = None
    current_revision: Optional[str] = None
    more_changes: Optional[bool] = Field(default=None, alias="_more_changes")

    @property
    def display_id(self) -> str:
        """Return display ID (number ID)"""
        return str(self.number)


class LabelInfo(BaseModel):
    """Label Info"""

    approved: Optional[Account] = None
    rejected: Optional[Account] = None
    recommended: Optional[Account] = None
    disliked: Optional[Account] = None
    value: Optional[int] = None
    default_value: Optional[int] = None
    values: Optional[dict[str, str]] = None
    all: Optional[list[dict[str, Any]]] = None


class MessageInfo(BaseModel):
    """Message Info"""

    id: str
    author: Optional[Account] = None
    date: str
    message: str
    tag: Optional[str] = None


class FileInfo(BaseModel):
    """File Info"""

    status: Optional[str] = None
    binary: Optional[bool] = None
    old_path: Optional[str] = None
    lines_inserted: Optional[int] = None
    lines_deleted: Optional[int] = None
    size_delta: Optional[int] = None
    size: Optional[int] = None


class ChangeDetail(Change):
    """Change Detail"""

    messages: Optional[list[MessageInfo]] = None
    labels: Optional[dict[str, LabelInfo]] = None
    permitted_labels: Optional[dict[str, list[str]]] = None
    reviewers: Optional[dict[str, list[Account]]] = None
    revisions: Optional[dict[str, Any]] = None


class CommentInfo(BaseModel):
    """Comment Info"""

    id: Optional[str] = None
    patch_set: Optional[int] = None
    path: Optional[str] = None
    side: Optional[str] = None
    line: Optional[int] = None
    range: Optional[dict[str, Any]] = None
    message: str
    updated: Optional[str] = None
    author: Optional[Account] = None
    unresolved: Optional[bool] = None
    in_reply_to: Optional[str] = None



class CommentRange(BaseModel):
    """Comment Range"""

    start_line: int
    start_character: int
    end_line: int
    end_character: int


class CommentInput(BaseModel):
    """Comment Input"""

    path: Optional[str] = None
    line: Optional[int] = None
    range: Optional[CommentRange] = None
    message: str
    side: str = "REVISION"
    in_reply_to: Optional[str] = None
    unresolved: Optional[bool] = None


class ReviewInput(BaseModel):
    """Review Request Input"""

    message: Optional[str] = None
    labels: Optional[dict[str, int]] = None
    comments: Optional[dict[str, list[CommentInput]]] = None
    tag: Optional[str] = None
    notify: Optional[str] = None
    drafts: Optional[str] = None
    ready: Optional[bool] = None
    work_in_progress: Optional[bool] = None


class ReviewResult(BaseModel):
    """Review Response Result"""

    labels: Optional[dict[str, int]] = None
    reviewers: Optional[dict[str, Any]] = None
    ready: Optional[bool] = None
