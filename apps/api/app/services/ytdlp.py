from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

from app.config import Settings
from app.errors import AppError
from app.models import FormatOption, ResolveResponse, TaskRecord, TaskStatus
from app.services.binaries import BinaryManager

DIRECT_PROTOCOLS = {"http", "https"}
DIRECT_EXTENSIONS = {"mp4", "m4v", "mov", "webm"}
SIDECAR_SUFFIXES = {
    ".part",
    ".ytdl",
    ".json",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".description",
    ".txt",
}


@dataclass
class DownloadOutcome:
    file_path: Path
    logs: List[str]


def _score_format(raw: Dict, direct_available: bool) -> tuple:
    height = int(raw.get("height") or 0)
    tbr = float(raw.get("tbr") or 0)
    filesize = int(raw.get("filesize") or raw.get("filesize_approx") or 0)
    ext = (raw.get("ext") or "").lower()
    return (
        height,
        1 if direct_available else 0,
        1 if ext == "mp4" else 0,
        filesize,
        tbr,
    )


def _quality_label(raw: Dict, resolution: str, ext: str) -> str:
    fps = raw.get("fps")
    pieces = [resolution, ext.upper()]
    if fps:
        pieces.append(f"{int(fps)} FPS")
    return " · ".join(pieces)


def _format_note(has_audio: bool, direct_available: bool) -> str:
    if direct_available:
        return "支持极速下载和稳定下载"
    if has_audio:
        return "服务端稳定下载"
    return "服务端下载，自动合并音频"


def build_format_candidates(info: Dict) -> List[FormatOption]:
    best_by_key: Dict[str, tuple] = {}
    raw_formats = info.get("formats") or []
    is_live = bool(info.get("is_live"))

    for raw in raw_formats:
        format_id = raw.get("format_id")
        format_url = raw.get("url")
        vcodec = raw.get("vcodec")
        acodec = raw.get("acodec")
        if not format_id or not format_url or vcodec == "none":
            continue

        ext = (raw.get("ext") or "mp4").lower()
        has_audio = acodec not in (None, "none")
        protocol = ((raw.get("protocol") or "").split("+")[0]).lower()
        direct_available = (
            not is_live
            and has_audio
            and protocol in DIRECT_PROTOCOLS
            and ext in DIRECT_EXTENSIONS
        )
        selector = format_id if has_audio else f"{format_id}+bestaudio/best"
        height = int(raw.get("height") or 0)
        resolution = f"{height}p" if height else (raw.get("format_note") or ext.upper())
        candidate = FormatOption(
            id=f"{format_id}:{'direct' if has_audio else 'mux'}",
            label=f"{resolution} · {ext.upper()}",
            container=ext,
            quality_label=_quality_label(raw, resolution, ext),
            resolution=resolution,
            height=height,
            approx_size_bytes=raw.get("filesize") or raw.get("filesize_approx"),
            direct_available=direct_available,
            requires_ffmpeg=not has_audio,
            note=_format_note(has_audio, direct_available),
            selector=selector,
            direct_url=format_url if direct_available else None,
            protocol=protocol,
        )

        key = f"{height}:{ext}:{has_audio}"
        current = best_by_key.get(key)
        score = _score_format(raw, direct_available)
        if current is None or score > current[0]:
            best_by_key[key] = (score, candidate)

    sorted_candidates = sorted(
        (value[1] for value in best_by_key.values()),
        key=lambda item: (
            item.height,
            1 if item.direct_available else 0,
            1 if item.container == "mp4" else 0,
            item.approx_size_bytes or 0,
        ),
        reverse=True,
    )
    return sorted_candidates[:8]


class YtDlpClient:
    def __init__(self, settings: Settings, binary_manager: BinaryManager) -> None:
        self.settings = settings
        self.binary_manager = binary_manager

    def resolve(self, url: str) -> ResolveResponse:
        yt_dlp = self.binary_manager.ensure_yt_dlp()
        command = [
            str(yt_dlp),
            "--dump-single-json",
            "--skip-download",
            "--no-playlist",
            "--no-warnings",
            "--windows-filenames",
            url,
        ]
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if completed.returncode != 0:
            raise self._map_error(completed.stderr or completed.stdout)

        try:
            info = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise AppError(502, "resolve_failed", "解析结果异常，未能读取视频信息。") from exc

        if info.get("_type") == "playlist" or info.get("entries"):
            raise AppError(400, "playlist_unsupported", "一期暂不支持播放列表或批量链接。")
        if info.get("is_live"):
            raise AppError(400, "live_unsupported", "一期暂不支持直播内容下载。")

        formats = build_format_candidates(info)
        if not formats:
            raise AppError(502, "resolve_failed", "当前链接未返回可下载的视频格式。")

        recommended = self._pick_recommended_format(formats)
        return ResolveResponse(
            source_url=str(info.get("webpage_url") or url),
            title=info.get("title") or "未命名视频",
            thumbnail_url=info.get("thumbnail"),
            duration_seconds=info.get("duration"),
            platform=info.get("extractor_key") or info.get("extractor") or "未知平台",
            uploader=info.get("uploader") or info.get("channel"),
            recommended_format_id=recommended.id,
            formats=formats,
        )

    def download(
        self,
        task: TaskRecord,
        on_progress: Callable[[Dict], None],
    ) -> DownloadOutcome:
        yt_dlp = self.binary_manager.ensure_yt_dlp()
        files_dir = self.settings.tasks_dir / task.task_id / "files"
        files_dir.mkdir(parents=True, exist_ok=True)

        command = [
            str(yt_dlp),
            "--newline",
            "--no-playlist",
            "--no-warnings",
            "--windows-filenames",
            "--no-write-info-json",
            "--no-write-thumbnail",
            "--no-write-comments",
            "--no-write-description",
            "-P",
            f"home:{files_dir}",
            "-P",
            f"temp:{self.settings.temp_dir}",
            "-o",
            "download.%(ext)s",
            "-f",
            task.selected_format.selector,
            "--progress-template",
            "download:%(progress._percent_str)s|%(progress._speed_str)s|%(progress._eta_str)s",
            task.source_url,
        ]

        if self.binary_manager.has_ffmpeg():
            command.extend(["--ffmpeg-location", str(self.settings.ffmpeg_path.parent)])

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        logs: List[str] = []
        if process.stdout is None:
            raise AppError(502, "download_failed", "下载任务启动失败。")

        for raw_line in process.stdout:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("download:"):
                on_progress(self._parse_progress(line))
                continue
            if "[Merger]" in line or "Merging formats into" in line:
                on_progress({"status": TaskStatus.postprocessing})
                continue
            logs.append(line)

        return_code = process.wait()
        if return_code != 0:
            raise self._map_error("\n".join(logs[-10:]))

        downloaded_file = self._find_downloaded_file(files_dir)
        if downloaded_file is None:
            raise AppError(502, "download_failed", "视频已下载，但未找到最终文件。")
        return DownloadOutcome(file_path=downloaded_file, logs=logs[-10:])

    def _find_downloaded_file(self, files_dir: Path) -> Optional[Path]:
        candidates = []
        for file in files_dir.iterdir():
            if not file.is_file():
                continue
            if file.suffix.lower() in SIDECAR_SUFFIXES:
                continue
            candidates.append(file)
        if not candidates:
            return None
        return max(candidates, key=lambda item: item.stat().st_size)

    def _pick_recommended_format(self, formats: List[FormatOption]) -> FormatOption:
        for candidate in formats:
            if candidate.direct_available and candidate.container == "mp4":
                return candidate
        for candidate in formats:
            if candidate.container == "mp4":
                return candidate
        return formats[0]

    def _parse_progress(self, line: str) -> Dict:
        _, payload = line.split("download:", 1)
        percent_text, speed_text, eta_text = (payload.split("|") + ["", "", ""])[:3]
        match = re.search(r"(\d+(?:\.\d+)?)%", percent_text)
        percent_value = float(match.group(1)) if match else 0.0
        eta_seconds: Optional[int] = None
        try:
            eta_seconds = int(eta_text.strip())
        except (TypeError, ValueError):
            eta_seconds = None
        return {
            "status": TaskStatus.downloading,
            "progress_percent": percent_value,
            "progress_text": percent_text.strip() or "0%",
            "speed_text": speed_text.strip() or None,
            "eta_seconds": eta_seconds,
        }

    def _map_error(self, raw_message: str) -> AppError:
        message = raw_message.lower()
        if "drm" in message:
            return AppError(403, "restricted_content", "检测到 DRM 保护内容，项目不会提供该类下载。")
        if any(keyword in message for keyword in ("login required", "sign in", "members-only", "premium")):
            return AppError(403, "restricted_content", "该内容需要登录或会员权限，一期不会处理此类链接。")
        if "unsupported url" in message:
            return AppError(400, "unsupported_url", "当前链接暂不受支持，请尝试其他公开视频链接。")
        if "playlist" in message:
            return AppError(400, "playlist_unsupported", "一期暂不支持播放列表或批量链接。")
        return AppError(502, "yt_dlp_failed", "下载内核处理失败，请稍后重试或更换链接。")

