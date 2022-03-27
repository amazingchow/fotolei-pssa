<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-12">
        <alert :message=message v-if="showMessage"></alert>
      </div>
    </div>
    <div class="row">
      <div class="col-sm-4">
      </div>
      <div class="col-sm-4">
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
      <div class="col-sm-4">
      </div>
    </div>
  </div>
</template>

<style>
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
          this.$cookies.set('logged', res.headers['set-logged'])
          this.$cookies.set('role', res.headers['set-role'])
          router.push('/')
        })
        .catch((_) => {
          // eslint-disable-next-line
          this.message = '登录失败，请检查账号和密码'
          this.showMessage = true
        })
    }
  },
  created () {
    console.log(process.env.NODE_ENV)
    console.log(process.env.SERVER_BASE_URL)
  }
}
</script>
