from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.config import Settings
from app.errors import AppError


@dataclass
class BinaryManager:
    settings: Settings

    def ensure_yt_dlp(self) -> Path:
        path = self.settings.yt_dlp_path
        if path.exists():
            return path
        raise AppError(
            503,
            "binary_missing",
            "未找到项目内 yt-dlp 二进制，请先运行 scripts/setup_binaries.py。",
        )

    def ensure_ffmpeg(self) -> Path:
        path = self.settings.ffmpeg_path
        if path.exists():
            return path
        raise AppError(
            503,
            "binary_missing",
            "未找到项目内 ffmpeg 二进制，请先运行 scripts/setup_binaries.py。",
        )

    def has_ffmpeg(self) -> bool:
        return self.settings.ffmpeg_path.exists()

