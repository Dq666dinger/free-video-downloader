<template>
  <div class="min-h-screen bg-cloud text-ink">
    <AppHeader />

    <main>
      <section id="console" class="relative overflow-hidden">
        <div class="absolute inset-0 bg-halo opacity-90"></div>
        <div class="mx-auto grid max-w-7xl gap-12 px-4 py-16 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:py-24">
          <div class="relative">
            <div class="inline-flex min-h-[40px] items-center rounded-full border border-accent/20 bg-white/80 px-4 text-sm font-semibold text-accent">
              合法公开内容下载工作台
            </div>
            <h1 class="mt-6 max-w-3xl font-display text-5xl font-bold tracking-tight text-ink sm:text-6xl">
              更快拿到视频文件，
              <span class="text-accent">在手机和电脑都顺手</span>
            </h1>
            <p class="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              面向学习和技术实践的轻量下载站。输入公开视频链接，先解析可用格式，再自动选择最优交付方式。
            </p>

            <div class="mt-8 flex flex-wrap gap-3">
              <div v-for="item in heroPills" :key="item" class="rounded-full bg-white px-4 py-2 text-sm text-slate-600 shadow-sm">
                {{ item }}
              </div>
            </div>

            <div class="mt-10 grid gap-4 sm:grid-cols-3">
              <article
                v-for="metric in heroMetrics"
                :key="metric.title"
                class="rounded-[26px] border border-white/70 bg-white/85 p-5 shadow-panel backdrop-blur"
              >
                <div class="text-sm font-semibold text-slate-500">{{ metric.title }}</div>
                <div class="mt-2 font-display text-3xl font-bold text-ink">{{ metric.value }}</div>
                <p class="mt-2 text-sm text-slate-500">{{ metric.caption }}</p>
              </article>
            </div>
          </div>

          <div class="relative rounded-[36px] border border-slate-800/10 bg-dusk p-6 text-white shadow-panel sm:p-8">
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-sm font-semibold uppercase tracking-[0.24em] text-blue-200">Download Console</p>
                <h2 class="mt-3 font-display text-3xl font-bold">一键解析视频链接</h2>
              </div>
              <div class="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs text-blue-100">
                24 小时临时领取
              </div>
            </div>

            <form class="mt-8 space-y-4" @submit.prevent="onResolve">
              <label class="block text-sm font-semibold text-blue-100" for="videoUrl">
                视频链接
              </label>
              <textarea
                id="videoUrl"
                v-model="url"
                rows="3"
                class="min-h-[120px] w-full rounded-[28px] border border-white/10 bg-white/8 px-5 py-4 text-base text-white placeholder:text-slate-400 focus:border-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-400/30"
                placeholder="粘贴公开视频链接，例如 https://example.com/watch?v=demo"
              />
              <div class="flex flex-col gap-3 sm:flex-row">
                <button
                  type="submit"
                  class="inline-flex min-h-[52px] items-center justify-center rounded-full bg-accent px-6 text-base font-semibold text-white transition hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-300 disabled:cursor-not-allowed disabled:opacity-60"
                  :disabled="resolving"
                >
                  {{ resolving ? '解析中...' : '开始解析' }}
                </button>
                <button
                  type="button"
                  class="inline-flex min-h-[52px] items-center justify-center rounded-full border border-white/15 px-6 text-base font-semibold text-white transition hover:bg-white/10"
                  @click="fillDemo"
                >
                  填充示例链接
                </button>
              </div>
            </form>

            <p v-if="errorMessage" class="mt-4 rounded-2xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
              {{ errorMessage }}
            </p>

            <div class="mt-6 rounded-[30px] border border-white/10 bg-white/6 p-5">
              <template v-if="resolved">
                <div class="flex flex-col gap-4 sm:flex-row">
                  <img
                    v-if="resolved.thumbnail_url"
                    :src="resolved.thumbnail_url"
                    :alt="resolved.title"
                    class="h-40 w-full rounded-[24px] object-cover sm:w-44"
                  />
                  <div class="min-w-0 flex-1">
                    <div class="text-sm font-semibold text-blue-200">{{ resolved.platform }}</div>
                    <h3 class="mt-2 font-display text-2xl font-bold leading-tight">{{ resolved.title }}</h3>
                    <div class="mt-3 flex flex-wrap gap-2 text-xs text-blue-100/90">
                      <span class="rounded-full bg-white/10 px-3 py-1">{{ formatDuration(resolved.duration_seconds) }}</span>
                      <span v-if="resolved.uploader" class="rounded-full bg-white/10 px-3 py-1">{{ resolved.uploader }}</span>
                      <span class="rounded-full bg-white/10 px-3 py-1">{{ resolved.formats.length }} 个可用格式</span>
                    </div>
                  </div>
                </div>

                <div class="mt-6 grid gap-3">
                  <FormatOptionCard
                    v-for="option in resolved.formats"
                    :key="option.id"
                    :option="option"
                    :active="option.id === selectedFormatId"
                    @select="selectedFormatId = option.id"
                  />
                </div>

                <div class="mt-6 flex flex-col gap-3 sm:flex-row">
                  <button
                    type="button"
                    class="inline-flex min-h-[52px] items-center justify-center rounded-full bg-white px-6 text-base font-semibold text-ink transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-60"
                    :disabled="creatingTask"
                    @click="onCreateTask"
                  >
                    {{ creatingTask ? '创建任务中...' : '开始下载任务' }}
                  </button>
                  <div class="rounded-full border border-white/10 px-4 py-3 text-sm text-blue-100">
                    默认先提供稳定下载，可用时追加极速下载。
                  </div>
                </div>
              </template>

              <template v-else>
                <div class="space-y-4">
                  <div class="rounded-[24px] border border-dashed border-white/15 px-5 py-6 text-sm leading-7 text-blue-100">
                    解析后会在这里展示视频封面、标题、清晰度、格式以及“是否支持极速下载”。
                  </div>
                  <div class="grid gap-3 sm:grid-cols-3">
                    <div v-for="placeholder in placeholders" :key="placeholder" class="rounded-[22px] bg-white/8 p-4">
                      <div class="text-sm font-semibold text-white">{{ placeholder }}</div>
                      <div class="mt-2 text-xs text-blue-100/80">主页先告诉你能不能下、怎么下、拿到什么格式。</div>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </section>

      <section id="features" class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 lg:py-12">
        <div class="grid gap-5 lg:grid-cols-4">
          <article v-for="feature in features" :key="feature.title" class="rounded-[30px] border border-slate-200 bg-white p-6 shadow-panel">
            <div class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-accent/10 text-accent">
              <component :is="feature.icon" class="h-6 w-6" />
            </div>
            <h2 class="mt-4 font-display text-2xl font-bold text-ink">{{ feature.title }}</h2>
            <p class="mt-3 text-sm leading-7 text-slate-600">{{ feature.description }}</p>
          </article>
        </div>
      </section>

      <section id="workflow" class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div class="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
          <div class="rounded-[32px] bg-white p-7 shadow-panel">
            <p class="text-sm font-semibold uppercase tracking-[0.24em] text-accent">Three-step flow</p>
            <h2 class="mt-4 font-display text-4xl font-bold text-ink">少做判断，先把视频拿到手</h2>
            <p class="mt-4 text-base leading-8 text-slate-600">
              一期不追求花哨功能，先把“解析成功、选格式、拿文件”做到明确、稳定、手机端顺手。
            </p>
          </div>

          <div class="grid gap-4">
            <article
              v-for="step in steps"
              :key="step.title"
              class="rounded-[30px] border border-slate-200 bg-white p-6 shadow-panel"
            >
              <div class="flex items-start gap-4">
                <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-dusk text-sm font-bold text-white">
                  {{ step.index }}
                </div>
                <div>
                  <h3 class="font-display text-2xl font-bold text-ink">{{ step.title }}</h3>
                  <p class="mt-2 text-sm leading-7 text-slate-600">{{ step.description }}</p>
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section id="compliance" class="mx-auto max-w-7xl px-4 pb-16 sm:px-6 lg:px-8">
        <div class="rounded-[36px] border border-amber-200 bg-amber-50 p-8 shadow-panel">
          <p class="text-sm font-semibold uppercase tracking-[0.24em] text-amber-700">Compliance First</p>
          <h2 class="mt-3 font-display text-3xl font-bold text-ink">只做合法公开内容下载，不碰灰区能力</h2>
          <div class="mt-6 grid gap-4 md:grid-cols-2">
            <div class="rounded-[24px] bg-white p-5">
              <h3 class="font-display text-xl font-bold text-ink">我们支持</h3>
              <p class="mt-3 text-sm leading-7 text-slate-600">
                公开可访问视频链接、单条视频任务、服务端稳定下载、条件成立时的极速下载、24 小时临时领取。
              </p>
            </div>
            <div class="rounded-[24px] bg-white p-5">
              <h3 class="font-display text-xl font-bold text-ink">我们拒绝</h3>
              <p class="mt-3 text-sm leading-7 text-slate-600">
                DRM、付费墙、登录态内容、Cookie 导入、平台风控规避、批量刷取与任何侵权用途。
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { CloudDownload, FolderKanban, ShieldCheck, Smartphone } from 'lucide-vue-next';
import { computed, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

import AppHeader from '@/components/AppHeader.vue';
import FormatOptionCard from '@/components/FormatOptionCard.vue';
import { ApiError, createTask, resolveVideo } from '@/lib/api';
import { formatDuration } from '@/lib/format';
import type { ResolveResponse } from '@/types';

const router = useRouter();

const url = ref('');
const resolving = ref(false);
const creatingTask = ref(false);
const errorMessage = ref('');
const resolved = ref<ResolveResponse | null>(null);
const resolvedInputUrl = ref('');
const selectedFormatId = ref('');

const heroPills = ['多平台公开内容', '手机端同样可领取', '自动最优交付方式'];
const placeholders = ['视频封面预览', '清晰度与容器', '交付模式判断'];

const heroMetrics = [
  { title: '交付模式', value: '2 种', caption: '稳定下载默认开启，极速下载条件启用。' },
  { title: '文件保留', value: '24h', caption: '下载完成后可在当前设备或临时链接中领取。' },
  { title: '一期原则', value: '轻量', caption: '无数据库，先跑通核心闭环，不额外堆功能。' }
];

const features = [
  {
    title: '稳定下载优先',
    description: '服务端先把文件落盘，再把真正可领的结果交给用户，桌面和移动端体验都更稳。',
    icon: FolderKanban
  },
  {
    title: '极速入口补充',
    description: '当格式天然支持直连时，自动补一个极速下载入口；不支持时不会强行展示。',
    icon: CloudDownload
  },
  {
    title: '手机端友好',
    description: '主操作区和结果卡都按单列手势区设计，按钮尺寸和信息密度都为移动端留足空间。',
    icon: Smartphone
  },
  {
    title: '合规边界清晰',
    description: '页面和接口都明确拒绝 DRM、会员内容、登录态导入和平台风控规避。',
    icon: ShieldCheck
  }
];

const steps = [
  {
    index: '01',
    title: '先解析再决定',
    description: '先拿到标题、封面、时长和可用格式，让用户清楚当前视频能不能下、能下到什么质量。'
  },
  {
    index: '02',
    title: '用明确格式创建任务',
    description: '从可选格式里直接选择，服务端重新校验并创建单条任务，避免前端状态和真实下载脱节。'
  },
  {
    index: '03',
    title: '按最优方式拿文件',
    description: '任务完成后优先给稳定下载；如果当前格式支持直连，再追加极速下载和临时领取链接。'
  }
];

const selectedFormat = computed(() =>
  resolved.value?.formats.find((option) => option.id === selectedFormatId.value) ?? null
);

function fillDemo() {
  url.value = 'https://samplelib.com/lib/preview/mp4/sample-5s.mp4';
}

async function onResolve() {
  const requestedUrl = url.value.trim();

  if (!requestedUrl) {
    errorMessage.value = '请先输入公开视频链接。';
    return;
  }

  resolving.value = true;
  errorMessage.value = '';

  try {
    const response = await resolveVideo(requestedUrl);
    if (url.value.trim() !== requestedUrl) {
      return;
    }
    resolved.value = response;
    resolvedInputUrl.value = requestedUrl;
    selectedFormatId.value = response.recommended_format_id;
  } catch (error) {
    if (url.value.trim() !== requestedUrl) {
      return;
    }
    if (error instanceof ApiError) {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = '解析失败，请稍后重试。';
    }
  } finally {
    resolving.value = false;
  }
}

async function onCreateTask() {
  if (!resolved.value || !selectedFormat.value) {
    errorMessage.value = '请先解析链接并选择一个格式。';
    return;
  }

  creatingTask.value = true;
  errorMessage.value = '';

  try {
    const task = await createTask(resolvedInputUrl.value, selectedFormat.value.id);
    await router.push({ name: 'task', params: { taskId: task.task_id } });
  } catch (error) {
    if (error instanceof ApiError) {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = '创建任务失败，请稍后重试。';
    }
  } finally {
    creatingTask.value = false;
  }
}

watch(url, (nextUrl) => {
  const trimmedUrl = nextUrl.trim();
  if (errorMessage.value) {
    errorMessage.value = '';
  }
  if (resolved.value && trimmedUrl !== resolvedInputUrl.value) {
    resolved.value = null;
    resolvedInputUrl.value = '';
    selectedFormatId.value = '';
  }
});
</script>
