import asyncio
from datetime import timedelta

import pytest

from app.config import Settings
from app.errors import AppError
from app.models import FormatOption, TaskRecord, TaskStatus
from app.services.binaries import BinaryManager
from app.services.task_store import TaskRepository, utcnow
from app.services.tasks import TaskService


class DummyYtDlpClient:
    pass


def build_settings(tmp_path):
    runtime_dir = tmp_path / 'runtime'
    bin_dir = runtime_dir / 'bin'
    tasks_dir = runtime_dir / 'tasks'
    temp_dir = runtime_dir / 'tmp'
    for path in (bin_dir, tasks_dir, temp_dir):
        path.mkdir(parents=True, exist_ok=True)
    return Settings(
        project_root=tmp_path,
        runtime_dir=runtime_dir,
        bin_dir=bin_dir,
        tasks_dir=tasks_dir,
        temp_dir=temp_dir,
        public_web_url='http://localhost:5173',
        cors_origins=['http://localhost:5173'],
        task_retention_hours=24,
        max_parallel_downloads=1,
        yt_dlp_path=bin_dir / 'yt-dlp.exe',
        ffmpeg_path=bin_dir / 'ffmpeg.exe',
        is_windows=True,
    )


def build_task(task_id: str) -> TaskRecord:
    now = utcnow()
    return TaskRecord(
        task_id=task_id,
        source_url='https://example.com/video',
        title='Sample Video',
        platform='Example',
        selected_format=FormatOption(
          id='22:direct',
          label='720p 路 MP4',
          container='mp4',
          quality_label='720p 路 MP4',
          resolution='720p',
          direct_available=True,
          requires_ffmpeg=False,
          selector='22',
          direct_url='https://cdn.example.com/video.mp4'
        ),
        status=TaskStatus.completed,
        direct_available=True,
        direct_url='https://cdn.example.com/video.mp4',
        output_path='runtime/tasks/demo/files/video.mp4',
        output_filename='video.mp4',
        created_at=now,
        updated_at=now,
        completed_at=now,
        expires_at=now + timedelta(hours=24),
    )


def build_service(tmp_path):
    settings = build_settings(tmp_path)
    repository = TaskRepository(settings)
    service = TaskService(settings, repository, BinaryManager(settings), DummyYtDlpClient())
    return repository, service


def test_build_download_response_rejects_expired_tasks(tmp_path):
    repository, service = build_service(tmp_path)
    expired = build_task('expired-download')
    expired.expires_at = utcnow() - timedelta(minutes=5)
    repository.save(expired)

    with pytest.raises(AppError) as exc_info:
        service.build_download_response(expired.task_id)

    service.shutdown()

    assert exc_info.value.status_code == 404
    assert repository.get(expired.task_id) is None


def test_build_direct_response_rejects_expired_tasks(tmp_path):
    repository, service = build_service(tmp_path)
    expired = build_task('expired-direct')
    expired.expires_at = utcnow() - timedelta(minutes=5)
    repository.save(expired)

    with pytest.raises(AppError) as exc_info:
        asyncio.run(service.build_direct_response(expired.task_id))

    service.shutdown()

    assert exc_info.value.status_code == 404
    assert repository.get(expired.task_id) is None
