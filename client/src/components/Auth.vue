<script lang="ts">

// some place holding code, need to be replaced
import { ref } from 'vue';

const username = ref('');
const password = ref('');

const handleLogin = async () => {
  if (!username.value || !password.value) {
    alert('Please fill all input fields...');
    return;
  }

  // Here you would usually use this data to send a login request to your server
  const data = {
    username: username.value,
    password: password.value
  }

  console.log(data);

  // Clear the form
  username.value = '';
  password.value = '';
}

</script>

<template>
  <div class="signin">
    <h2>Sign In</h2>
    <form @submit.prevent="handleLogin">
      <div>
        <label for="username">Username:</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">Sign In</button>
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