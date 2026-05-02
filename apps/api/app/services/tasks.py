from __future__ import annotations

import re
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from typing import Optional

import httpx
from fastapi import Request
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse

from app.config import Settings
from app.errors import AppError
from app.models import ResolveResponse, TaskAcceptedResponse, TaskRecord, TaskResponse, TaskStatus
from app.services.binaries import BinaryManager
from app.services.task_store import TaskRepository, utcnow
from app.services.ytdlp import DownloadOutcome, YtDlpClient


def _safe_download_name(title: str, extension: str) -> str:
    stem = re.sub(r"[\\/:*?\"<>|]+", "_", title).strip(" .") or "video"
    return f"{stem}.{extension}"


class TaskService:
    def __init__(
        self,
        settings: Settings,
        repository: TaskRepository,
        binary_manager: BinaryManager,
        yt_client: YtDlpClient,
    ) -> None:
        self.settings = settings
        self.repository = repository
        self.binary_manager = binary_manager
        self.yt_client = yt_client
        self.executor = ThreadPoolExecutor(
            max_workers=settings.max_parallel_downloads,
            thread_name_prefix="video-download",
        )
        self._lock = threading.RLock()

    def shutdown(self) -> None:
        try:
            self.executor.shutdown(wait=False, cancel_futures=True)
        except TypeError:
            self.executor.shutdown(wait=False)

    def resolve_url(self, url: str) -> ResolveResponse:
        self.repository.cleanup_expired()
        return self.yt_client.resolve(url)

    def create_task(self, url: str, format_id: str) -> TaskAcceptedResponse:
        self.repository.cleanup_expired()
        resolved = self.yt_client.resolve(url)
        selected = next((item for item in resolved.formats if item.id == format_id), None)
        if selected is None:
            raise AppError(400, "invalid_format", "所选格式已失效，请重新解析视频链接。")
        if selected.requires_ffmpeg:
            self.binary_manager.ensure_ffmpeg()

        task_id = uuid.uuid4().hex
        now = utcnow()
        task = TaskRecord(
            task_id=task_id,
            source_url=resolved.source_url,
            title=resolved.title,
            platform=resolved.platform,
            thumbnail_url=resolved.thumbnail_url,
            duration_seconds=resolved.duration_seconds,
            selected_format=selected,
            status=TaskStatus.pending,
            direct_available=selected.direct_available,
            direct_url=selected.direct_url,
            created_at=now,
            updated_at=now,
            expires_at=now + timedelta(hours=self.settings.task_retention_hours),
        )
        self.repository.save(task)
        self.executor.submit(self._run_download, task_id)
        return TaskAcceptedResponse(task_id=task_id, status=TaskStatus.pending)

    def get_task_response(self, task_id: str, request: Request) -> TaskResponse:
        task = self._require_task(task_id, cleanup_expired=True)
        return self._to_public_task(task, request)

    def build_download_response(self, task_id: str) -> FileResponse:
        task = self._require_task(task_id, cleanup_expired=True)
        if task.status != TaskStatus.completed or not task.output_path or not task.output_filename:
            raise AppError(409, "task_incomplete", "任务尚未完成，暂时无法领取文件。")
        file_path = Path(task.output_path)
        if not file_path.exists():
            raise AppError(410, "file_expired", "文件已过期或已被清理，请重新创建任务。")
        return FileResponse(
            file_path,
            media_type="application/octet-stream",
            filename=task.output_filename,
        )

    async def build_direct_response(self, task_id: str, mode: str = "redirect"):
        task = self._require_task(task_id, cleanup_expired=True)
        if not task.direct_available or not task.direct_url:
            raise AppError(404, "direct_unavailable", "当前格式不支持极速下载。")
        if mode == "proxy":
            return await self._proxy_direct_download(task)
        return RedirectResponse(task.direct_url, status_code=307)

    def _require_task(self, task_id: str, *, cleanup_expired: bool = False) -> TaskRecord:
        if cleanup_expired:
            self.repository.cleanup_expired()
        task = self.repository.get(task_id)
        if task is None:
            raise AppError(404, "task_not_found", "未找到对应任务，可能已过期。")
        return task

    def _to_public_task(self, task: TaskRecord, request: Request) -> TaskResponse:
        base = str(request.base_url).rstrip("/")
        stable_url = None
        if task.status == TaskStatus.completed and task.output_path:
            stable_url = f"{base}/api/tasks/{task.task_id}/download"
        direct_url = None
        if task.direct_available and task.direct_url:
            direct_url = f"{base}/api/tasks/{task.task_id}/direct"
        share_url = f"{self.settings.public_web_url}/task/{task.task_id}"

        return TaskResponse(
            task_id=task.task_id,
            status=task.status,
            title=task.title,
            source_url=task.source_url,
            platform=task.platform,
            thumbnail_url=task.thumbnail_url,
            duration_seconds=task.duration_seconds,
            selected_format=task.selected_format,
            progress_percent=task.progress_percent,
            progress_text=task.progress_text,
            speed_text=task.speed_text,
            eta_seconds=task.eta_seconds,
            error_message=task.error_message,
            stable_download_url=stable_url,
            direct_download_url=direct_url,
            share_url=share_url,
            expires_at=task.expires_at,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
        )

    def _run_download(self, task_id: str) -> None:
        task = self._require_task(task_id)
        task.status = TaskStatus.downloading
        task.updated_at = utcnow()
        self.repository.save(task)
        try:
            outcome = self.yt_client.download(task, lambda payload: self._apply_progress(task_id, payload))
            self._mark_completed(task_id, outcome)
        except AppError as exc:
            self._mark_failed(task_id, exc.message)
        except Exception:
            self._mark_failed(task_id, "后台下载过程中发生异常，请稍后重试。")

    def _apply_progress(self, task_id: str, payload: dict) -> None:
        with self._lock:
            task = self._require_task(task_id)
            task.status = payload.get("status", task.status)
            task.progress_percent = payload.get("progress_percent", task.progress_percent)
            task.progress_text = payload.get("progress_text", task.progress_text)
            task.speed_text = payload.get("speed_text", task.speed_text)
            task.eta_seconds = payload.get("eta_seconds", task.eta_seconds)
            task.updated_at = utcnow()
            self.repository.save(task)

    def _mark_completed(self, task_id: str, outcome: DownloadOutcome) -> None:
        with self._lock:
            task = self._require_task(task_id)
            extension = outcome.file_path.suffix.lstrip(".") or task.selected_format.container
            task.status = TaskStatus.completed
            task.progress_percent = 100.0
            task.progress_text = "100%"
            task.output_path = str(outcome.file_path)
            task.output_filename = _safe_download_name(task.title, extension)
            task.logs = outcome.logs
            task.completed_at = utcnow()
            task.updated_at = task.completed_at
            task.speed_text = None
            task.eta_seconds = None
            self.repository.save(task)

    def _mark_failed(self, task_id: str, message: str) -> None:
        with self._lock:
            task = self._require_task(task_id)
            task.status = TaskStatus.failed
            task.error_message = message
            task.updated_at = utcnow()
            self.repository.save(task)

    async def _proxy_direct_download(self, task: TaskRecord) -> StreamingResponse:
        client = httpx.AsyncClient(follow_redirects=True, timeout=None)
        upstream = await client.send(
            client.build_request("GET", task.direct_url),
            stream=True,
        )
        if upstream.status_code >= 400:
            await upstream.aclose()
            await client.aclose()
            raise AppError(502, "direct_proxy_failed", "极速下载代理失败，请改用稳定下载。")

        async def iterator():
            try:
                async for chunk in upstream.aiter_bytes():
                    yield chunk
            finally:
                await upstream.aclose()
                await client.aclose()

        headers = {}
        for key in ("content-length", "content-type", "content-disposition", "accept-ranges"):
            value = upstream.headers.get(key)
            if value:
                headers[key] = value
        return StreamingResponse(iterator(), headers=headers, media_type=upstream.headers.get("content-type"))
