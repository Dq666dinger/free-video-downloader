<template>
  <div class="min-h-screen bg-cloud text-ink">
    <AppHeader />

    <main class="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <RouterLink class="inline-flex items-center gap-2 text-sm font-semibold text-accent transition hover:opacity-80" to="/">
        返回首页
      </RouterLink>

      <div v-if="errorMessage" class="mt-6 rounded-[28px] border border-rose-200 bg-rose-50 px-6 py-5 text-sm text-rose-700">
        {{ errorMessage }}
      </div>

      <template v-else-if="task">
        <section class="mt-6 grid gap-8 lg:grid-cols-[1.05fr_0.95fr]">
          <article class="rounded-[36px] bg-dusk p-7 text-white shadow-panel sm:p-8">
            <div class="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p class="text-sm font-semibold uppercase tracking-[0.24em] text-blue-200">Task overview</p>
                <h1 class="mt-3 font-display text-4xl font-bold">{{ task.title }}</h1>
              </div>
              <StatusBadge :status="task.status" />
            </div>

            <div class="mt-6 flex flex-wrap gap-3 text-sm text-blue-100">
              <span class="rounded-full bg-white/10 px-3 py-2">{{ task.platform }}</span>
              <span class="rounded-full bg-white/10 px-3 py-2">{{ task.selected_format.label }}</span>
              <span class="rounded-full bg-white/10 px-3 py-2">文件保留到 {{ formatExpiry(task.expires_at) }}</span>
            </div>

            <div class="mt-8 rounded-[28px] border border-white/10 bg-white/7 p-5">
              <div class="flex items-center justify-between gap-4">
                <div>
                  <p class="text-sm font-semibold text-blue-100">当前进度</p>
                  <h2 class="mt-1 font-display text-3xl font-bold">{{ task.progress_text }}</h2>
                </div>
                <div class="text-right text-sm text-blue-100">
                  <div>{{ task.speed_text || '速度待计算' }}</div>
                  <div class="mt-1">{{ formatEta(task.eta_seconds) }}</div>
                </div>
              </div>
              <div class="mt-5 h-3 overflow-hidden rounded-full bg-white/10">
                <div class="h-full rounded-full bg-gradient-to-r from-accent to-blue-300" :style="{ width: `${task.progress_percent}%` }"></div>
              </div>
              <p v-if="task.error_message" class="mt-4 rounded-2xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
                {{ task.error_message }}
              </p>
            </div>
          </article>

          <div class="space-y-5">
            <DeliveryOptionCard
              eyebrow="稳定交付"
              title="服务端下载完成后领取"
              description="优先推荐的获取方式。服务端先把文件准备好，再给你稳定可用的下载入口。"
            >
              <template #badge>
                <span class="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">默认主入口</span>
              </template>
              <a
                v-if="task.stable_download_url"
                :href="task.stable_download_url"
                class="inline-flex min-h-[48px] items-center justify-center rounded-full bg-accent px-5 text-sm font-semibold text-white transition hover:opacity-90"
              >
                下载稳定文件
              </a>
              <span v-else class="inline-flex min-h-[48px] items-center rounded-full bg-slate-100 px-5 text-sm font-semibold text-slate-500">
                任务完成后可领取
              </span>
            </DeliveryOptionCard>

            <DeliveryOptionCard
              eyebrow="极速入口"
              title="直接跳转或代理下载"
              description="仅在当前格式具备直连条件时开放。若站点直连体验不稳定，可切换到代理模式。"
            >
              <template #badge>
                <span
                  :class="task.direct_download_url ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-500'"
                  class="rounded-full px-3 py-1 text-xs font-semibold"
                >
                  {{ task.direct_download_url ? '已可用' : '条件不满足' }}
                </span>
              </template>

              <template v-if="task.direct_download_url">
                <a
                  :href="task.direct_download_url"
                  class="inline-flex min-h-[48px] items-center justify-center rounded-full border border-accent px-5 text-sm font-semibold text-accent transition hover:bg-accent hover:text-white"
                >
                  极速直连
                </a>
                <a
                  :href="`${task.direct_download_url}?mode=proxy`"
                  class="inline-flex min-h-[48px] items-center justify-center rounded-full bg-slate-100 px-5 text-sm font-semibold text-slate-700 transition hover:bg-slate-200"
                >
                  代理下载
                </a>
              </template>
            </DeliveryOptionCard>

            <DeliveryOptionCard
              eyebrow="跨端领取"
              title="24 小时临时任务链接"
              description="复制这个任务链接，可以在手机和电脑之间切换继续领取，不需要登录。"
            >
              <template #badge>
                <span class="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700">24h 有效</span>
              </template>
              <div class="w-full rounded-[24px] bg-slate-50 px-4 py-3 text-sm text-slate-600">
                {{ task.share_url }}
              </div>
              <button
                type="button"
                class="inline-flex min-h-[48px] items-center justify-center rounded-full bg-ink px-5 text-sm font-semibold text-white transition hover:opacity-90"
                @click="copyShareUrl"
              >
                {{ copied ? '已复制链接' : '复制任务链接' }}
              </button>
            </DeliveryOptionCard>
          </div>
        </section>

        <section class="mt-10 grid gap-5 lg:grid-cols-3">
          <article class="rounded-[30px] border border-slate-200 bg-white p-6 shadow-panel">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">源链接</p>
            <p class="mt-3 break-all text-sm leading-7 text-slate-600">{{ task.source_url }}</p>
          </article>
          <article class="rounded-[30px] border border-slate-200 bg-white p-6 shadow-panel">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">格式说明</p>
            <p class="mt-3 text-sm leading-7 text-slate-600">{{ task.selected_format.note }}</p>
          </article>
          <article class="rounded-[30px] border border-slate-200 bg-white p-6 shadow-panel">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">状态刷新</p>
            <p class="mt-3 text-sm leading-7 text-slate-600">
              {{ terminal ? '任务已结束，页面停止轮询。' : '任务进行中，页面会自动刷新状态。' }}
            </p>
          </article>
        </section>
      </template>

      <div v-else class="mt-12 rounded-[32px] border border-slate-200 bg-white p-10 text-center shadow-panel">
        <div class="font-display text-3xl font-bold text-ink">正在加载任务...</div>
        <p class="mt-3 text-sm text-slate-500">稍等片刻，任务信息会自动出现。</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';

import AppHeader from '@/components/AppHeader.vue';
import DeliveryOptionCard from '@/components/DeliveryOptionCard.vue';
import StatusBadge from '@/components/StatusBadge.vue';
import { ApiError, getTask } from '@/lib/api';
import { formatEta, formatExpiry } from '@/lib/format';
import type { TaskResponse } from '@/types';

const route = useRoute();
const task = ref<TaskResponse | null>(null);
const errorMessage = ref('');
const copied = ref(false);
let pollTimer: number | null = null;

const terminal = computed(() =>
  task.value ? ['completed', 'failed'].includes(task.value.status) : false
);

async function loadTask() {
  const taskId = String(route.params.taskId || '');
  if (!taskId || taskId === 'demo') {
    errorMessage.value = '请先从首页创建真实下载任务。';
    return;
  }

  try {
    task.value = await getTask(taskId);
    errorMessage.value = '';
    schedulePoll();
  } catch (error) {
    if (error instanceof ApiError) {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = '读取任务失败，请稍后刷新重试。';
    }
  }
}

function clearPoll() {
  if (pollTimer) {
    window.clearTimeout(pollTimer);
    pollTimer = null;
  }
}

function schedulePoll() {
  clearPoll();
  if (terminal.value) {
    return;
  }
  pollTimer = window.setTimeout(() => {
    void loadTask();
  }, 2500);
}

async function copyShareUrl() {
  if (!task.value) {
    return;
  }
  if (!navigator.clipboard) {
    copied.value = false;
    return;
  }
  await navigator.clipboard.writeText(task.value.share_url);
  copied.value = true;
  window.setTimeout(() => {
    copied.value = false;
  }, 1800);
}

watch(
  () => route.params.taskId,
  () => {
    task.value = null;
    errorMessage.value = '';
    void loadTask();
  }
);

onMounted(() => {
  void loadTask();
});

onBeforeUnmount(() => {
  clearPoll();
});
</script>
