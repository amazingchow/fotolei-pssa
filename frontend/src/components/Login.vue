<template>
  <div class="container-fluid">
    <alert :message=message v-if="showMessage"></alert>
    <div class="row">
      <div class="col-sm-8" id="logo-area">
        <h1 id="logo">FOTOLEI PSSA SYSTEM</h1>
      </div>
      <div class="col-sm-4" id="login-form-area">
        <b-form id="login-form">
          <b-form-group
            label="账号"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
            >
            <b-form-input v-model="loginForm.username"></b-form-input>
          </b-form-group>
          <b-form-group
            label="密码"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
            >
            <b-form-input v-model="loginForm.password" type="password"></b-form-input>
          </b-form-group>
          <br/>
          <div id="login-btn" class="w-100 d-block">
            <b-button variant="dark" @click="onLogin">登录</b-button>
          </div>
        </b-form>
      </div>
    </div>
  </div>
</template>

<style>
#logo-area {
  display: flex;
  justify-content: center;
}

#logo {
  margin-top: 200px;
}

#login-form-area {
  display: flex;
  justify-content: center;
}

#login-form {
  margin-top: 200px;
  max-width: 300px;
}

#login-btn {
  text-align: right;
}
</style>

<script>
import axios from 'axios'
import Alert from './Alert.vue'
import router from '../router'

export default {
  data () {
    return {
      serverBaseURL: process.env.SERVER_BASE_URL,

      loginForm: {
        username: '',
        password: ''
      },

      showMessage: false
    }
  },
  components: {
    alert: Alert
  },
  methods: {
    async onLogin () {
      let payload = {
        username: this.loginForm.username,
        password: this.loginForm.password
      }
      await axios.post(this.serverBaseURL + '/api/v1/users/login', payload)
        .then((res) => {
          this.$cookies.set('logged', res.headers['set-logged'].split('=')[1])
          this.$cookies.set('username', res.headers['set-user'].split('=')[1])
          this.$cookies.set('role', res.headers['set-role'].split('=')[1])
          router.push('/')
        })
        .catch((error) => {
          if (error.response.status === 401) {
            this.message = '登录失败，账号未注册！'
            this.showMessage = true
          } else if (error.response.status === 404) {
            this.message = '登录失败，请检查账号和密码！'
            this.showMessage = true
          } else if (error.response.status === 409) {
            this.message = '禁止重复登录！'
            this.showMessage = true
          } else {
            // eslint-disable-next-line
            console.log(error)
            router.push('/500')
          }
        })
    }
  },
  created () {
    console.log(process.env.NODE_ENV)
    console.log(process.env.SERVER_BASE_URL)
  }
}
</script>
