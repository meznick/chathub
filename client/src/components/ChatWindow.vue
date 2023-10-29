<script setup lang="ts">

import { useChatStore } from "../stores/chat.ts";

const store = useChatStore()

function sendMessage() {
  // code for sending message to server here
  console.log('sending ' + store.newMessage)
  store.saveMessage()
}

</script>

<template>
  <div id="app">
    <div class="chat-window">
      <div v-for="message in store.messages" :key="message.id" class="chat-message">
        {{ message.text }}
      </div>
    </div>
    <div class="chat-input">
      <input v-model="store.newMessage" placeholder="Type your message..." @keyup.enter="sendMessage">
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<style scoped>

</style>
