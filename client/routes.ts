import { createRouter, createWebHistory } from "vue-router";
import Chat from "./src/components/Chat.vue";
import Auth from "./src/components/Auth.vue";
import UserProfile from "./src/components/UserProfile.vue"

const routes = [
  { path: "/", component: Chat },
  { path: "/login", component: Auth },
  { path: '/register', component: Auth },
  { path: "/user", component: UserProfile },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
