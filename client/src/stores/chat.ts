import { defineStore } from "pinia";
import { ref } from "vue";

type Message = {
    id: number;
    text: string;
};

export const useChatStore = defineStore('chatStore', () => {
    const messages = ref<Message[]>([])
    const messagesCounter = ref<number>(0)
    const newMessage = ref<string>('')
    function saveMessage(){
      if (newMessage.value.trim() === '') return;
      messages.value.push({
          id: messagesCounter.value,
          text: newMessage.value.trim()
      });
      messagesCounter.value++;
      newMessage.value = '';
    }
    return { messages, newMessage, saveMessage}
})
