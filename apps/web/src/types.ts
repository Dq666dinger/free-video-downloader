export type TaskStatus = 'pending' | 'downloading' | 'postprocessing' | 'completed' | 'failed';

export interface FormatOption {
  id: string;
  label: string;
  container: string;
  quality_label: string;
  resolution: string;
  height: number;
  approx_size_bytes: number | null;
  direct_available: boolean;
  requires_ffmpeg: boolean;
  note: string | null;
}

export interface ResolveResponse {
  source_url: string;
  title: string;
  thumbnail_url: string | null;
  duration_seconds: number | null;
  platform: string;
  uploader: string | null;
  recommended_format_id: string;
  formats: FormatOption[];
}

export interface TaskAcceptedResponse {
  task_id: string;
  status: TaskStatus;
}

export interface TaskResponse {
  task_id: string;
  status: TaskStatus;
  title: string;
  source_url: string;
  platform: string;
  thumbnail_url: string | null;
  duration_seconds: number | null;
  selected_format: FormatOption;
  progress_percent: number;
  progress_text: string;
  speed_text: string | null;
  eta_seconds: number | null;
  error_message: string | null;
  stable_download_url: string | null;
  direct_download_url: string | null;
  share_url: string;
  expires_at: string;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

