<template>
  <button
    type="button"
    class="group flex min-h-[128px] w-full cursor-pointer flex-col justify-between rounded-3xl border p-4 text-left transition"
    :class="
      active
        ? 'border-accent bg-accent/5 shadow-glow'
        : 'border-slate-200 bg-white hover:-translate-y-0.5 hover:border-accent/40 hover:shadow-panel'
    "
    @click="$emit('select')"
  >
    <div class="flex items-start justify-between gap-3">
      <div>
        <div class="font-display text-base font-semibold text-ink">{{ option.label }}</div>
        <div class="mt-1 text-sm text-slate-500">{{ option.quality_label }}</div>
      </div>
      <span
        v-if="option.direct_available"
        class="rounded-full bg-emerald-100 px-2 py-1 text-[11px] font-semibold text-emerald-700"
      >
        极速
      </span>
    </div>
    <div class="space-y-2">
      <div class="text-xs text-slate-500">{{ option.note }}</div>
      <div class="flex flex-wrap gap-2 text-[11px] text-slate-500">
        <span class="rounded-full bg-slate-100 px-2 py-1">{{ option.container.toUpperCase() }}</span>
        <span v-if="option.requires_ffmpeg" class="rounded-full bg-amber-100 px-2 py-1 text-amber-700">需合并音频</span>
      </div>
    </div>
  </button>
</template>

<script setup lang="ts">
import type { FormatOption } from '@/types';

defineProps<{
  option: FormatOption;
  active: boolean;
}>();

defineEmits<{
  (event: 'select'): void;
}>();
</script>

