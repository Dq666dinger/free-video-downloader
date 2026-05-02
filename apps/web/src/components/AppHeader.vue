<template>
  <header class="sticky top-0 z-30 border-b border-white/70 bg-white/80 backdrop-blur">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
      <RouterLink class="flex items-center gap-3" to="/">
        <span class="flex h-11 w-11 items-center justify-center rounded-2xl bg-dusk text-sm font-semibold text-white shadow-glow">
          VH
        </span>
        <div>
          <div class="font-display text-lg font-bold text-ink">Video Harvest</div>
          <div class="text-xs text-slate-500">合法内容下载工作台</div>
        </div>
      </RouterLink>

      <nav class="hidden items-center gap-8 text-sm text-slate-600 md:flex">
        <a class="transition hover:text-accent" href="#features">核心价值</a>
        <a class="transition hover:text-accent" href="#workflow">使用流程</a>
        <a class="transition hover:text-accent" href="#compliance">合规边界</a>
      </nav>

      <RouterLink
        class="inline-flex min-h-[44px] items-center justify-center rounded-full bg-accent px-5 text-sm font-semibold text-white transition hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        :to="{ path: '/', hash: '#console' }"
      >
        立即解析
      </RouterLink>
    </div>
  </header>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
</script>
