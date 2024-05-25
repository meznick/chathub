<script lang="ts">

// some place holding code, need to be replaced
import { ref, watch } from 'vue';
import { useAuthStore } from "../stores/auth.ts";
import { useRouter } from "vue-router";

export default {
  setup() {
    const authStore = useAuthStore();
    const username = ref('');
    const password = ref('');
    const password1 = ref('');
    const password2 = ref('');
    const alreadyRegistered = ref(false);

    const router = useRouter();

    watch(alreadyRegistered, () => {
      if ( alreadyRegistered.value ) {
        // switching to login page
        router.push('/login')
      } else {
        // switching to register page
        router.push('/register')
      }
    })

    const handleLogin = async () => {
      if (!username.value || !password.value) {
        alert('Please fill all input fields...');
        return;
      }

      // Here you would usually use this data to send a login request to your server
      authStore.$patch((state) => {
        state.loginFormData.username = username.value;
        state.loginFormData.password = password.value;
      });
      const authSuccess: boolean = authStore.authorize();

      if ( authSuccess ) {
        // Clear the form
        username.value = '';
        password.value = '';
      } else {
        // show alert or something
      }
    }

    const handleRegistration = async () => {
      if (!username.value || !password1.value || (password1.value != password2.value)) {
        alert('Fix your username or passwords');
        return;
      }

      authStore.$patch((state) => {
        state.registerFormData.username = username.value;
        state.registerFormData.password1 = password1.value;
        state.registerFormData.password2 = password2.value;
      });
      const registerSuccess: boolean = authStore.register();

      if ( registerSuccess ) {
        username.value = '';
        password1.value = '';
        password2.value = '';
        alreadyRegistered.value = true;
      } else {
        // show alert or something
      }
    }

    return {
      username,
      password,
      password1,
      password2,
      handleLogin,
      handleRegistration,
      alreadyRegistered,
    }
  }
}
</script>

<template>
  <div v-if="!alreadyRegistered" class="register">
    <h2>Register</h2>
    <form @submit.prevent="handleRegistration">
      <div>
        <label for="username">Username</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div>
        <label for="password1">Password</label>
        <input type="password" id="password1" v-model="password1" required />
      </div>
      <div>
        <label for="password2">Repeat Password</label>
        <input type="password" id="password2" v-model="password2" required />
      </div>
      <button type="submit">Register</button>
      <button @click="alreadyRegistered = !alreadyRegistered">Already registered</button>
    </form>
  </div>
  <div v-else class="signin">
    <h2>Sign In</h2>
    <form @submit.prevent="handleLogin">
      <div>
        <label for="username">Username</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div>
        <label for="password">Password</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">Sign In</button>
      <button @click="alreadyRegistered = !alreadyRegistered">Register</button>
    </form>
  </div>
</template>

<style scoped>
.signin {
  width: 300px;
  margin: 0 auto;
}

.signin form div {
  margin: 10px 0;
}

.signin form button {
  width: 100%;
  padding: 10px;
}
</style>
