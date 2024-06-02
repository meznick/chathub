<script setup lang="ts">

import Chat from "./components/Chat.vue";
import Auth from "./components/Auth.vue";
import { useAuthStore } from "./stores/auth.ts";
import { useGeneralStore } from "./stores/general.ts";

import config from "../config.json"

const authStore = useAuthStore()
const generalStore = useGeneralStore()

generalStore.parseConfig(config)
</script>

<template>
  <Chat v-if="authStore.isUserAuthorized"/>
  <Auth v-else />
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
