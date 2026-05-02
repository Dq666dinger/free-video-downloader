import type { ResolveResponse, TaskAcceptedResponse, TaskResponse } from '@/types';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {})
    },
    ...init
  });

  if (!response.ok) {
    const fallback = '请求失败，请稍后重试。';
    try {
      const payload = await response.json();
      throw new ApiError(payload.message || fallback, response.status);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(fallback, response.status);
    }
  }

  return (await response.json()) as T;
}

export function resolveVideo(url: string) {
  return request<ResolveResponse>('/api/resolve', {
    method: 'POST',
    body: JSON.stringify({ url })
  });
}

export function createTask(url: string, formatId: string) {
  return request<TaskAcceptedResponse>('/api/tasks', {
    method: 'POST',
    body: JSON.stringify({ url, format_id: formatId })
  });
}

export function getTask(taskId: string) {
  return request<TaskResponse>(`/api/tasks/${taskId}`);
}

export function buildApiUrl(path: string | null | undefined) {
  return path ? path : '';
}

