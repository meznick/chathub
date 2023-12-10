<script setup lang="ts">

import { useChatStore } from "../stores/chat.ts";
import { SocketClient, MessagePayload } from "../utils/socket_client.ts"

const store = useChatStore()
const socket_client = new SocketClient('test', 'ws://localhost:4321')
socket_client.handshakeServer()

function sendMessage() {
  console.log('sending ' + store.newMessage)
  let payload: MessagePayload = {"message": store.newMessage}
  socket_client.sendMessage(JSON.stringify(payload))
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
