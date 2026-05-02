from __future__ import annotations

import json
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import Settings
from app.models import TaskRecord


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TaskRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._lock = threading.RLock()

    def _task_dir(self, task_id: str) -> Path:
        return self.settings.tasks_dir / task_id

    def _task_file(self, task_id: str) -> Path:
        return self._task_dir(task_id) / "task.json"

    def ensure_task_dirs(self, task_id: str) -> tuple[Path, Path]:
        task_dir = self._task_dir(task_id)
        files_dir = task_dir / "files"
        with self._lock:
            files_dir.mkdir(parents=True, exist_ok=True)
        return task_dir, files_dir

    def save(self, task: TaskRecord) -> TaskRecord:
        task_dir, _ = self.ensure_task_dirs(task.task_id)
        target = task_dir / "task.json"
        tmp_file = task_dir / "task.json.tmp"
        payload = task.model_dump(mode="json")
        payload["selected_format"]["selector"] = task.selected_format.selector
        payload["selected_format"]["direct_url"] = task.selected_format.direct_url
        payload["selected_format"]["protocol"] = task.selected_format.protocol
        with self._lock:
            tmp_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp_file.replace(target)
        return task

    def get(self, task_id: str) -> Optional[TaskRecord]:
        target = self._task_file(task_id)
        if not target.exists():
            return None
        with self._lock:
            return TaskRecord.model_validate_json(target.read_text(encoding="utf-8"))

    def cleanup_expired(self) -> None:
        now = utcnow()
        with self._lock:
            for task_dir in self.settings.tasks_dir.iterdir():
                if not task_dir.is_dir():
                    continue
                task_file = task_dir / "task.json"
                if not task_file.exists():
                    continue
                try:
                    task = TaskRecord.model_validate_json(task_file.read_text(encoding="utf-8"))
                except Exception:
                    shutil.rmtree(task_dir, ignore_errors=True)
                    continue
                if task.expires_at <= now:
                    shutil.rmtree(task_dir, ignore_errors=True)
