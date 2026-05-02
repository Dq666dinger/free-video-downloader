export function formatDuration(seconds: number | null) {
  if (!seconds) {
    return '未知时长';
  }
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remain = seconds % 60;
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m ${remain}s`;
}

export function formatBytes(value: number | null) {
  if (!value) {
    return '大小未知';
  }
  const units = ['B', 'KB', 'MB', 'GB'];
  let current = value;
  let unit = 0;
  while (current >= 1024 && unit < units.length - 1) {
    current /= 1024;
    unit += 1;
  }
  return `${current.toFixed(current >= 10 || unit === 0 ? 0 : 1)} ${units[unit]}`;
}

export function formatEta(seconds: number | null) {
  if (!seconds && seconds !== 0) {
    return 'ETA 待计算';
  }
  const minutes = Math.floor(seconds / 60);
  const remain = seconds % 60;
  if (minutes <= 0) {
    return `${remain}s`;
  }
  return `${minutes}m ${remain}s`;
}

export function formatExpiry(isoString: string) {
  const date = new Date(isoString);
  return new Intl.DateTimeFormat('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
}

