# 一期接口契约

## 基础说明

- Base URL：默认 `http://localhost:8000`
- 数据格式：`application/json`
- 前端默认来源：`http://localhost:5173`

## 1. 解析视频

### `POST /api/resolve`

请求体：

```json
{
  "url": "https://example.com/watch?v=demo"
}
```

成功响应示例：

```json
{
  "source_url": "https://example.com/watch?v=demo",
  "title": "Demo Video",
  "thumbnail_url": "https://image.example.com/poster.jpg",
  "duration_seconds": 120,
  "platform": "Youtube",
  "uploader": "Uploader",
  "recommended_format_id": "22:direct",
  "formats": [
    {
      "id": "22:direct",
      "label": "720p · MP4",
      "container": "mp4",
      "quality_label": "720p · MP4 · 30 FPS",
      "resolution": "720p",
      "height": 720,
      "approx_size_bytes": 52428800,
      "direct_available": true,
      "requires_ffmpeg": false,
      "note": "支持极速下载和稳定下载"
    }
  ]
}
```

关键字段说明：

- `recommended_format_id`
  前端默认高亮的推荐格式。
- `direct_available`
  当前格式是否支持极速下载。
- `requires_ffmpeg`
  当前格式是否依赖音视频合并。

## 2. 创建下载任务

### `POST /api/tasks`

请求体：

```json
{
  "url": "https://example.com/watch?v=demo",
  "format_id": "22:direct"
}
```

成功响应：

```json
{
  "task_id": "f7c5d1d52d6d4f79b9f4f02d57dce4a0",
  "status": "pending"
}
```

## 3. 查询任务

### `GET /api/tasks/{taskId}`

成功响应示例：

```json
{
  "task_id": "f7c5d1d52d6d4f79b9f4f02d57dce4a0",
  "status": "completed",
  "title": "Demo Video",
  "source_url": "https://example.com/watch?v=demo",
  "platform": "Youtube",
  "thumbnail_url": "https://image.example.com/poster.jpg",
  "duration_seconds": 120,
  "selected_format": {
    "id": "22:direct",
    "label": "720p · MP4",
    "container": "mp4",
    "quality_label": "720p · MP4 · 30 FPS",
    "resolution": "720p",
    "height": 720,
    "approx_size_bytes": 52428800,
    "direct_available": true,
    "requires_ffmpeg": false,
    "note": "支持极速下载和稳定下载"
  },
  "progress_percent": 100,
  "progress_text": "100%",
  "speed_text": null,
  "eta_seconds": null,
  "error_message": null,
  "stable_download_url": "http://localhost:8000/api/tasks/f7.../download",
  "direct_download_url": "http://localhost:8000/api/tasks/f7.../direct",
  "share_url": "http://localhost:5173/task/f7...",
  "expires_at": "2026-05-03T08:00:00+00:00",
  "created_at": "2026-05-02T08:00:00+00:00",
  "updated_at": "2026-05-02T08:02:00+00:00",
  "completed_at": "2026-05-02T08:02:00+00:00"
}
```

关键行为：

- `stable_download_url`
  仅在任务完成且文件仍存在时返回。
- `direct_download_url`
  仅在所选格式满足极速下载条件时返回。
- `share_url`
  前端任务详情页链接，用于 24 小时跨端领取。

## 4. 稳定下载

### `GET /api/tasks/{taskId}/download`

行为：

- 返回服务端已落盘的视频文件流。
- 如果任务未完成，返回 `409`
- 如果文件已被清理，返回 `410`

## 5. 极速下载

### `GET /api/tasks/{taskId}/direct`

默认行为：

- `mode=redirect`
  返回 307 跳转到媒体直链

可选行为：

- `mode=proxy`
  由后端代理返回下载流

请求示例：

```text
GET /api/tasks/{taskId}/direct
GET /api/tasks/{taskId}/direct?mode=proxy
```

## 错误格式

统一错误格式：

```json
{
  "error": "task_not_found",
  "message": "未找到对应任务，可能已过期。"
}
```

常见错误码：

- `400`
  - `invalid_format`
  - `playlist_unsupported`
  - `unsupported_url`
- `403`
  - `restricted_content`
- `404`
  - `task_not_found`
  - `direct_unavailable`
- `409`
  - `task_incomplete`
- `410`
  - `file_expired`
- `502`
  - `resolve_failed`
  - `yt_dlp_failed`
  - `direct_proxy_failed`
- `503`
  - `binary_missing`

