from __future__ import annotations

import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


YT_DLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
FFMPEG_ZIP_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-gpl.zip"


def download(url: str, destination: Path) -> None:
    with urllib.request.urlopen(url) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)


def install_windows_binaries(project_root: Path) -> None:
    bin_dir = project_root / "runtime" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    yt_target = bin_dir / "yt-dlp.exe"
    ffmpeg_target = bin_dir / "ffmpeg.exe"
    ffprobe_target = bin_dir / "ffprobe.exe"

    print("Downloading yt-dlp...")
    download(YT_DLP_URL, yt_target)

    with tempfile.TemporaryDirectory() as tmp_dir:
        archive_path = Path(tmp_dir) / "ffmpeg.zip"
        print("Downloading ffmpeg...")
        download(FFMPEG_ZIP_URL, archive_path)
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.namelist():
                lowered = member.lower()
                if lowered.endswith("/ffmpeg.exe"):
                    with archive.open(member) as source, ffmpeg_target.open("wb") as output:
                        shutil.copyfileobj(source, output)
                if lowered.endswith("/ffprobe.exe"):
                    with archive.open(member) as source, ffprobe_target.open("wb") as output:
                        shutil.copyfileobj(source, output)

    print(f"Binaries installed into {bin_dir}")


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    if sys.platform != "win32":
        print("This bootstrapper currently targets Windows. Please place yt-dlp and ffmpeg in runtime/bin manually.")
        return 1
    install_windows_binaries(project_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
