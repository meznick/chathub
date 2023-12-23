import { defineStore } from "pinia";
import { ref } from "vue";

export type Message = {
    id: number;
    text: string;
    author_id: string;
};

export const useChatStore = defineStore('chatStore', () => {
    const messages = ref<Message[]>([])
    const messagesCounter = ref<number>(0)
    const newMessage = ref<string>('')
    function saveMessage(author_id: string){
      if (newMessage.value.trim() === '') return;
      messages.value.push({
          id: messagesCounter.value,
          text: newMessage.value.trim(),
          author_id: author_id,
      });
      messagesCounter.value++;
      newMessage.value = '';
    }
    return { messages, newMessage, saveMessage}
})
