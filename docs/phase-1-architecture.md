# 一期工程结构与数据流

## 目录结构

```text
apps/
  api/
    app/
      main.py
      config.py
      models.py
      errors.py
      services/
        binaries.py
        task_store.py
        tasks.py
        ytdlp.py
    tests/
  web/
    src/
      components/
      views/
      router/
      lib/
runtime/
  bin/
  tasks/
  tmp/
scripts/
  setup_binaries.py
docs/
```

## 前端职责

### 首页 `apps/web/src/views/HomeView.vue`

- 承担产品化展示与主操作入口。
- 调用 `/api/resolve` 获取视频元信息和格式列表。
- 根据 `recommended_format_id` 默认选中推荐格式。
- 调用 `/api/tasks` 创建后台下载任务。
- 创建成功后跳转 `/task/:taskId`。

### 任务页 `apps/web/src/views/TaskView.vue`

- 调用 `/api/tasks/{taskId}` 轮询任务状态。
- 当任务完成时展示：
  - 稳定下载入口
  - 极速直连入口
  - 代理下载入口
  - 临时领取链接
- 当任务失败时展示错误信息。

## 后端职责

### `app/main.py`

- 创建 FastAPI 应用
- 注册 CORS
- 注册接口
- 注册统一异常处理

### `services/binaries.py`

- 检测 `runtime/bin/` 下的 `yt-dlp` 和 `ffmpeg`
- 在缺失时抛出友好错误，提示先运行二进制下载脚本

### `services/ytdlp.py`

- 封装 `yt-dlp` 调用
- 负责：
  - 解析元信息
  - 清洗格式列表
  - 判断某格式是否支持极速下载
  - 启动真实下载子进程
  - 解析下载进度

### `services/task_store.py`

- 用本地 JSON 持久化任务
- 路径格式：
  - `runtime/tasks/<taskId>/task.json`
  - `runtime/tasks/<taskId>/files/*`
- 负责到期任务清理

### `services/tasks.py`

- 负责下载任务生命周期管理
- 负责：
  - 创建任务
  - 提交到线程池执行
  - 维护任务状态
  - 输出稳定下载和极速下载入口
  - 代理极速下载

## 下载数据流

### 解析流程

1. 前端提交视频 URL 到 `/api/resolve`
2. 后端调用 `yt-dlp --dump-single-json --no-playlist --skip-download`
3. 后端筛选可用格式并生成前端友好的格式列表
4. 前端展示格式选项和推荐项

### 创建任务流程

1. 前端提交 `url + format_id` 到 `/api/tasks`
2. 后端重新解析一次 URL，避免前端缓存格式失效
3. 后端校验所选格式
4. 后端创建 `task.json`
5. 后端将真实下载提交到线程池

### 稳定下载流程

1. 后端下载文件到 `runtime/tasks/<taskId>/files/`
2. 任务完成后记录 `output_path` 和 `output_filename`
3. 前端通过 `/api/tasks/{taskId}/download` 领取文件

### 极速下载流程

1. 解析阶段如果发现当前格式：
  - 有音频
  - 协议为 `http/https`
  - 容器是可直接交付的视频容器
2. 则标记 `direct_available = true`
3. 任务详情页补充 `/api/tasks/{taskId}/direct`
4. 支持两种模式：
  - `redirect`
  - `proxy`

## 任务状态模型

- `pending`
- `downloading`
- `postprocessing`
- `completed`
- `failed`

## 本地文件设计

### 二进制目录

- `runtime/bin/yt-dlp.exe`
- `runtime/bin/ffmpeg.exe`
- `runtime/bin/ffprobe.exe`

### 任务目录

每个任务单独一个目录：

```text
runtime/tasks/<taskId>/
  task.json
  files/
    download.mp4
```

## 当前技术债

- 当前没有下载并发队列可视化能力，只有线程池控制。
- 当前没有真正的任务列表页和回收站页。
- 当前没有任务恢复/重试按钮。
- 当前错误文案与页面中文本存在统一整理空间。
- 当前生命周期关闭事件建议后续切换到 FastAPI lifespan。

