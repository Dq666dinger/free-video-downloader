from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import List


def _split_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    project_root: Path
    runtime_dir: Path
    bin_dir: Path
    tasks_dir: Path
    temp_dir: Path
    public_web_url: str
    cors_origins: List[str]
    task_retention_hours: int
    max_parallel_downloads: int
    yt_dlp_path: Path
    ffmpeg_path: Path
    is_windows: bool

    @classmethod
    def from_env(cls) -> "Settings":
        project_root = Path(__file__).resolve().parents[3]
        runtime_dir = project_root / "runtime"
        bin_dir = runtime_dir / "bin"
        tasks_dir = runtime_dir / "tasks"
        temp_dir = runtime_dir / "tmp"
        is_windows = platform.system().lower().startswith("win")
        yt_binary = "yt-dlp.exe" if is_windows else "yt-dlp"
        ffmpeg_binary = "ffmpeg.exe" if is_windows else "ffmpeg"

        for path in (runtime_dir, bin_dir, tasks_dir, temp_dir):
            path.mkdir(parents=True, exist_ok=True)

        public_web_url = os.getenv("PUBLIC_WEB_URL", "http://localhost:5173").rstrip("/")
        cors_env = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )

        return cls(
            project_root=project_root,
            runtime_dir=runtime_dir,
            bin_dir=bin_dir,
            tasks_dir=tasks_dir,
            temp_dir=temp_dir,
            public_web_url=public_web_url,
            cors_origins=_split_csv(cors_env),
            task_retention_hours=int(os.getenv("TASK_RETENTION_HOURS", "24")),
            max_parallel_downloads=int(os.getenv("MAX_PARALLEL_DOWNLOADS", "2")),
            yt_dlp_path=bin_dir / yt_binary,
            ffmpeg_path=bin_dir / ffmpeg_binary,
            is_windows=is_windows,
        )

