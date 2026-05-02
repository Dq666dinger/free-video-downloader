from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class TaskStatus(str, Enum):
    pending = "pending"
    downloading = "downloading"
    postprocessing = "postprocessing"
    completed = "completed"
    failed = "failed"


class FormatOption(BaseModel):
    id: str
    label: str
    container: str
    quality_label: str
    resolution: str
    height: int = 0
    approx_size_bytes: Optional[int] = None
    direct_available: bool = False
    requires_ffmpeg: bool = False
    note: Optional[str] = None
    selector: str = Field(exclude=True)
    direct_url: Optional[str] = Field(default=None, exclude=True)
    protocol: Optional[str] = Field(default=None, exclude=True)


class ResolveRequest(BaseModel):
    url: HttpUrl


class ResolveResponse(BaseModel):
    source_url: str
    title: str
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    platform: str
    uploader: Optional[str] = None
    recommended_format_id: str
    formats: List[FormatOption]


class CreateTaskRequest(BaseModel):
    url: HttpUrl
    format_id: str


class TaskAcceptedResponse(BaseModel):
    task_id: str
    status: TaskStatus


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    title: str
    source_url: str
    platform: str
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    selected_format: FormatOption
    progress_percent: float = 0
    progress_text: str = "0%"
    speed_text: Optional[str] = None
    eta_seconds: Optional[int] = None
    error_message: Optional[str] = None
    stable_download_url: Optional[str] = None
    direct_download_url: Optional[str] = None
    share_url: str
    expires_at: datetime
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class TaskRecord(BaseModel):
    task_id: str
    source_url: str
    title: str
    platform: str
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    selected_format: FormatOption
    status: TaskStatus
    progress_percent: float = 0
    progress_text: str = "0%"
    speed_text: Optional[str] = None
    eta_seconds: Optional[int] = None
    error_message: Optional[str] = None
    direct_available: bool = False
    direct_url: Optional[str] = None
    output_path: Optional[str] = None
    output_filename: Optional[str] = None
    logs: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    expires_at: datetime

