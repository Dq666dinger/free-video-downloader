from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import Settings
from app.errors import AppError
from app.models import CreateTaskRequest, ResolveRequest, TaskAcceptedResponse, TaskResponse
from app.services.binaries import BinaryManager
from app.services.task_store import TaskRepository
from app.services.tasks import TaskService
from app.services.ytdlp import YtDlpClient


def build_task_service(settings: Settings) -> TaskService:
    repository = TaskRepository(settings)
    binaries = BinaryManager(settings)
    yt_client = YtDlpClient(settings, binaries)
    return TaskService(settings, repository, binaries, yt_client)


def create_app() -> FastAPI:
    settings = Settings.from_env()
    task_service = build_task_service(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        finally:
            request_service: TaskService = app.state.task_service
            request_service.shutdown()

    app = FastAPI(
        title="Universal Video Downloader API",
        version="1.0.0",
        description="Lightweight backend for the universal video downloader MVP.",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.task_service = task_service

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "message": "服务内部发生异常，请稍后重试。"},
        )

    def get_task_service(request: Request) -> TaskService:
        return request.app.state.task_service

    @app.get("/")
    async def root():
        return {"name": "universal-video-downloader-api", "version": "1.0.0"}

    @app.post("/api/resolve")
    async def resolve_video(
        payload: ResolveRequest,
        service: TaskService = Depends(get_task_service),
    ):
        return service.resolve_url(str(payload.url))

    @app.post("/api/tasks", response_model=TaskAcceptedResponse)
    async def create_task(
        payload: CreateTaskRequest,
        service: TaskService = Depends(get_task_service),
    ):
        return service.create_task(str(payload.url), payload.format_id)

    @app.get("/api/tasks/{task_id}", response_model=TaskResponse)
    async def get_task(
        task_id: str,
        request: Request,
        service: TaskService = Depends(get_task_service),
    ):
        return service.get_task_response(task_id, request)

    @app.get("/api/tasks/{task_id}/download")
    async def download_task_file(
        task_id: str,
        service: TaskService = Depends(get_task_service),
    ):
        return service.build_download_response(task_id)

    @app.get("/api/tasks/{task_id}/direct")
    async def direct_download(
        task_id: str,
        mode: str = Query("redirect", pattern="^(redirect|proxy)$"),
        service: TaskService = Depends(get_task_service),
    ):
        return await service.build_direct_response(task_id, mode=mode)

    return app


app = create_app()
