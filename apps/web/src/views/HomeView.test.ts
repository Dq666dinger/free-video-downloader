import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/vue';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createRouter, createWebHistory } from 'vue-router';

import HomeView from '@/views/HomeView.vue';

function buildRouter() {
  return createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', component: HomeView },
      { path: '/task/:taskId', component: { template: '<div />' } }
    ]
  });
}

describe('HomeView', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  it('parses a link and shows the returned format options', async () => {
    const fetchMock = vi
      .spyOn(global, 'fetch')
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          source_url: 'https://example.com/video',
          title: 'Demo Video',
          thumbnail_url: 'https://image.example.com/poster.jpg',
          duration_seconds: 90,
          platform: 'Example',
          uploader: 'Uploader',
          recommended_format_id: '22:direct',
          formats: [
            {
              id: '22:direct',
              label: '720p 路 MP4',
              container: 'mp4',
              quality_label: '720p 路 MP4',
              resolution: '720p',
              height: 720,
              approx_size_bytes: null,
              direct_available: true,
              requires_ffmpeg: false,
              note: '鏀寔鏋侀€熶笅杞藉拰绋冲畾涓嬭浇'
            }
          ]
        })
      } as Response);

    render(HomeView, {
      global: {
        plugins: [buildRouter()]
      }
    });

    await fireEvent.update(
      screen.getByPlaceholderText('粘贴公开视频链接，例如 https://example.com/watch?v=demo'),
      'https://example.com/video'
    );
    await fireEvent.click(screen.getByRole('button', { name: '开始解析' }));

    await waitFor(() => {
      expect(screen.getByText('Demo Video')).toBeInTheDocument();
      expect(screen.getAllByText('720p 路 MP4').length).toBeGreaterThan(0);
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('clears stale resolve results when the input URL changes', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        source_url: 'https://example.com/video',
        title: 'Demo Video',
        thumbnail_url: 'https://image.example.com/poster.jpg',
        duration_seconds: 90,
        platform: 'Example',
        uploader: 'Uploader',
        recommended_format_id: '22:direct',
        formats: [
          {
            id: '22:direct',
            label: '720p 路 MP4',
            container: 'mp4',
            quality_label: '720p 路 MP4',
            resolution: '720p',
            height: 720,
            approx_size_bytes: null,
            direct_available: true,
            requires_ffmpeg: false,
            note: '鏀寔鏋侀€熶笅杞藉拰绋冲畾涓嬭浇'
          }
        ]
      })
    } as Response);

    render(HomeView, {
      global: {
        plugins: [buildRouter()]
      }
    });

    const input = screen.getByPlaceholderText('粘贴公开视频链接，例如 https://example.com/watch?v=demo');
    await fireEvent.update(input, 'https://example.com/video');
    await fireEvent.click(screen.getByRole('button', { name: '开始解析' }));

    await waitFor(() => {
      expect(screen.getByText('Demo Video')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: '开始下载任务' })).toBeInTheDocument();
    });

    await fireEvent.update(input, 'https://example.com/other-video');

    await waitFor(() => {
      expect(screen.queryByText('Demo Video')).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: '开始下载任务' })).not.toBeInTheDocument();
    });
  });
});
