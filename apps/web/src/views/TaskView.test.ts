import { render, screen, waitFor } from '@testing-library/vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createRouter, createWebHistory } from 'vue-router';

import TaskView from '@/views/TaskView.vue';

describe('TaskView', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders download options once the task is completed', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({
        task_id: 'task-1',
        status: 'completed',
        title: 'Demo Video',
        source_url: 'https://example.com/video',
        platform: 'Example',
        thumbnail_url: null,
        duration_seconds: 95,
        selected_format: {
          id: '22:direct',
          label: '720p · MP4',
          container: 'mp4',
          quality_label: '720p · MP4',
          resolution: '720p',
          height: 720,
          approx_size_bytes: null,
          direct_available: true,
          requires_ffmpeg: false,
          note: '支持极速下载和稳定下载'
        },
        progress_percent: 100,
        progress_text: '100%',
        speed_text: null,
        eta_seconds: null,
        error_message: null,
        stable_download_url: 'http://localhost:8000/api/tasks/task-1/download',
        direct_download_url: 'http://localhost:8000/api/tasks/task-1/direct',
        share_url: 'http://localhost:5173/task/task-1',
        expires_at: '2026-05-03T08:00:00+00:00',
        created_at: '2026-05-02T08:00:00+00:00',
        updated_at: '2026-05-02T08:02:00+00:00',
        completed_at: '2026-05-02T08:02:00+00:00'
      })
    } as Response);

    const router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div />' } },
        { path: '/task/:taskId', component: TaskView }
      ]
    });
    router.push('/task/task-1');
    await router.isReady();

    render(TaskView, {
      global: {
        plugins: [router]
      }
    });

    await waitFor(() => {
      expect(screen.getByText('Demo Video')).toBeInTheDocument();
      expect(screen.getByRole('link', { name: '下载稳定文件' })).toBeInTheDocument();
      expect(screen.getByRole('link', { name: '极速直连' })).toBeInTheDocument();
    });
  });
});
