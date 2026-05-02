<template>
  <span :class="classes">{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import type { TaskStatus } from '@/types';

const props = defineProps<{
  status: TaskStatus;
}>();

const palette = {
  pending: 'bg-slate-100 text-slate-700',
  downloading: 'bg-blue-100 text-blue-700',
  postprocessing: 'bg-amber-100 text-amber-700',
  completed: 'bg-emerald-100 text-emerald-700',
  failed: 'bg-rose-100 text-rose-700'
} satisfies Record<TaskStatus, string>;

const labels = {
  pending: '排队中',
  downloading: '下载中',
  postprocessing: '后处理中',
  completed: '已完成',
  failed: '失败'
} satisfies Record<TaskStatus, string>;

const classes = computed(
  () =>
    `inline-flex min-h-[36px] items-center rounded-full px-3 text-xs font-semibold ${palette[props.status]}`
);

const label = computed(() => labels[props.status]);
</script>

