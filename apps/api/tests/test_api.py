from datetime import timedelta

from fastapi.testclient import TestClient

from app.main import create_app
from app.models import (
    FormatOption,
    ResolveResponse,
    TaskAcceptedResponse,
    TaskResponse,
    TaskStatus,
)
from app.services.task_store import utcnow


class FakeTaskService:
    def resolve_url(self, url: str) -> ResolveResponse:
        return ResolveResponse(
            source_url=url,
            title="Demo Video",
            thumbnail_url="https://image.example.com/poster.jpg",
            duration_seconds=120,
            platform="Example",
            uploader="Uploader",
            recommended_format_id="22:direct",
            formats=[
                FormatOption(
                    id="22:direct",
                    label="720p · MP4",
                    container="mp4",
                    quality_label="720p · MP4",
                    resolution="720p",
                    direct_available=True,
                    requires_ffmpeg=False,
                    selector="22",
                    direct_url="https://cdn.example.com/video.mp4",
                )
            ],
        )

    def create_task(self, url: str, format_id: str) -> TaskAcceptedResponse:
        return TaskAcceptedResponse(task_id="task-1", status=TaskStatus.pending)

    def get_task_response(self, task_id, request) -> TaskResponse:
        now = utcnow()
        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.completed,
            title="Demo Video",
            source_url="https://example.com/video",
            platform="Example",
            thumbnail_url="https://image.example.com/poster.jpg",
            duration_seconds=120,
            selected_format=FormatOption(
                id="22:direct",
                label="720p · MP4",
                container="mp4",
                quality_label="720p · MP4",
                resolution="720p",
                direct_available=True,
                requires_ffmpeg=False,
                selector="22",
                direct_url="https://cdn.example.com/video.mp4",
            ),
            progress_percent=100,
            progress_text="100%",
            stable_download_url="http://testserver/api/tasks/task-1/download",
            direct_download_url="http://testserver/api/tasks/task-1/direct",
            share_url="http://localhost:5173/task/task-1",
            expires_at=now + timedelta(hours=24),
            created_at=now,
            updated_at=now,
            completed_at=now,
        )

    def shutdown(self):
        return None


def test_resolve_and_task_routes():
    app = create_app()
    app.state.task_service = FakeTaskService()
    client = TestClient(app)

    resolve_response = client.post("/api/resolve", json={"url": "https://example.com/video"})
    assert resolve_response.status_code == 200
    assert resolve_response.json()["recommended_format_id"] == "22:direct"

    create_response = client.post(
        "/api/tasks",
        json={"url": "https://example.com/video", "format_id": "22:direct"},
    )
    assert create_response.status_code == 200
    assert create_response.json()["task_id"] == "task-1"

    task_response = client.get("/api/tasks/task-1")
    assert task_response.status_code == 200
    data = task_response.json()
    assert data["stable_download_url"].endswith("/api/tasks/task-1/download")
    assert data["direct_download_url"].endswith("/api/tasks/task-1/direct")

