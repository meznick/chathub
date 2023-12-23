import { createApp } from 'vue'
import { createPinia } from "pinia";
import './style.css'
import App from './App.vue'
import {router} from "../routes.ts";

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
