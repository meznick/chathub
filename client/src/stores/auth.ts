import { defineStore } from 'pinia';

export const useAuthStore = defineStore('authStore', {
  state: () => {
    const localStorageCurrentUser = localStorage.getItem('current_user');
    return {
      currentUser: localStorageCurrentUser ? JSON.parse(localStorageCurrentUser) : null,
      loginFormData: defaultLoginFormData,
      registerFormData: defaultRegisterFormData,
    }
  },

  getters: {
    isUserAuthorized: (state) => state.currentUser !== null
  },

  actions: {
    authorize(): boolean {
      let ok = true;

      fetch('/login', {
        method: 'POST',
        headers: new Headers({'Content-Type': 'application/json'}),
        body: JSON.stringify({
          username: this.loginFormData.username,
          password: this.loginFormData.password
        })
      }).then(response => {
        return { 'status': response.status, data: response.json() }
      }).then(data => {
        console.log(data.status, data.data)
        if ( data.status !== 200 ) {
          data.data.then(json => {
            console.log(`Got status ${data.status} with data: ${json.detail}`)
          })
          ok = false;
        } else {
          console.log('JWT cookie saved!')
          data.data.then(json => {
            this.currentUser = json;
            localStorage.setItem('current_user', JSON.stringify(json));
          })
        }
      }).catch((error) => {
        console.error(`Request failed: ${error}`)
        ok = false;
      })

      return ok;
    },
    register(): boolean {
      let ok = true;

      fetch('/register', {
        method: 'POST',
        headers: new Headers({'Content-Type': 'application/json'}),
        body: JSON.stringify({
          username: this.registerFormData.username,
          password1: this.registerFormData.password1,
          password2: this.registerFormData.password2,
        })
      }).then(response => {
        return { 'status': response.status, data: response.json() }
      }).then(data => {
        if ( data.status !== 200 ) {
          data.data.then(json => {
            console.log(`Got status ${data.status} with data: ${json}`)
            ok = false;
          })
        } else {
          console.log('Registration successful, redirecting to login page')
        }
      }).catch((error) => {
        console.error(`Request failed: ${error}`)
        ok = false;
      })

      return ok;
    }
  }
});

interface LoginFormData {
  username: string,
  password: string
}

const defaultLoginFormData: LoginFormData = {
  username: "",
  password: ""
}

interface RegisterFormData {
  username: string,
  password1: string,
  password2: string
}

const defaultRegisterFormData: RegisterFormData = {
  username: '',
  password1: '',
  password2: ''
}
