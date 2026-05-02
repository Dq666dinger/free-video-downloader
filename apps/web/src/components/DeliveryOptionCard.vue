<template>
  <article class="rounded-[28px] border border-slate-200 bg-white p-5 shadow-panel">
    <div class="flex items-start justify-between gap-4">
      <div>
        <p class="text-sm font-semibold text-slate-500">{{ eyebrow }}</p>
        <h3 class="mt-1 font-display text-xl font-bold text-ink">{{ title }}</h3>
      </div>
      <slot name="badge" />
    </div>
    <p class="mt-3 text-sm leading-6 text-slate-600">{{ description }}</p>
    <div class="mt-5 flex flex-wrap gap-3">
      <slot />
    </div>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  eyebrow: string;
  title: string;
  description: string;
}>();
</script>

