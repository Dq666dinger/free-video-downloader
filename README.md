# Universal Video Downloader

一个面向学习、技术实践和合法公开内容下载的轻量视频下载网站一期实现。

## 技术栈

- 前端：`Vue 3 + Vite + Tailwind CSS`
- 后端：`FastAPI + yt-dlp + ffmpeg`
- 存储：本地任务目录，无数据库

## 当前能力

- 解析单条公开视频链接
- 展示标题、封面、时长、平台和可用格式
- 创建单任务下载并轮询进度
- 默认提供稳定下载
- 条件满足时提供极速直连和代理下载
- 提供 24 小时临时任务链接

## 目录结构

```text
apps/
  api/   FastAPI 后端
  web/   Vue 3 前端
runtime/
  bin/   yt-dlp / ffmpeg 二进制
  tasks/ 任务文件
  tmp/   临时文件
scripts/
  setup_binaries.py
```

## 启动前准备

1. 安装前端依赖

```powershell
cd apps/web
npm.cmd install
```

2. 安装后端依赖

```powershell
cd apps/api
python -m pip install -r requirements-dev.txt
```

3. 下载项目内二进制

```powershell
cd ../..
python scripts/setup_binaries.py
```

## 启动项目

后端：

```powershell
cd apps/api
uvicorn main:app --reload --port 8000
```

前端：

```powershell
cd apps/web
npm.cmd run dev -- --host 0.0.0.0 --port 5173
```

## 测试命令

后端：

```powershell
cd apps/api
python -m pytest
```

前端：

```powershell
cd apps/web
npm.cmd run test:run
```

## 合规说明

本项目只面向合法公开内容下载，不支持：

- DRM 保护内容
- 付费墙 / 会员专享内容
- 登录态导入
- Cookie 注入
- 平台风控规避
- 批量抓取与侵权用途
