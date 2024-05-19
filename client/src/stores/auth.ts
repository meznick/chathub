import { defineStore } from 'pinia';

export const useAuthStore = defineStore('authStore', {
  state: () => {
    return {
      currentUser: defaultUserInfo,
      loginFormData: defaultLoginFormData
    }
  },

  getters: {
    isUserAuthorized: (state) => state.currentUser.username !== null
  },

  actions: {
    authorize() {
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
            console.log(json.detail)
          })
        } else {
          // store jwt token somewhere
        }
      }).catch((error) => {
        console.log(`Request failed: ${error}`)
      })
    }
  }
});

interface UserInfo {
  username: string | null
}

const defaultUserInfo: UserInfo = {
  username: null
}

interface LoginFormData {
  username: string,
  password: string
}

const defaultLoginFormData: LoginFormData = {
  username: "",
  password: ""
}
