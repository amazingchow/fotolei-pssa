<template>
  <div class="row">
    <div class="col-sm-12">
      <b-navbar type="dark" variant="dark">
        <b-navbar-brand href="#">Fotolei PssA</b-navbar-brand>
        <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>
        <b-collapse id="nav-collapse" is-nav>
          <b-navbar-nav>
            <b-nav-item href="/product">商品明细库</b-nav-item>
            <b-nav-item href="/">库存明细库</b-nav-item>
            <b-nav-item href="/slist">辅助查询</b-nav-item>
            <b-nav-item href="/oplog">操作日志</b-nav-item>
            <b-nav-item href="/user" v-if="showUserManagementModule">用户管理</b-nav-item>
          </b-navbar-nav>
          <b-navbar-nav class="ml-auto">
            <b-nav-item-dropdown right>
              <!-- Using 'button-content' slot -->
              <template #button-content>
                <em>{{ username }}</em>
              </template>
              <b-dropdown-item variant="dark" @click="onLogout">登出</b-dropdown-item>
            </b-nav-item-dropdown>
          </b-navbar-nav>
        </b-collapse>
      </b-navbar>
  </div>
</div>
</template>

<script>
import axios from 'axios'
import router from '../router'

export default {
  data () {
    return {
      serverBaseURL: process.env.SERVER_BASE_URL,

      username: 'anonymous'
    }
  },
  methods: {
    async onLogout () {
      await axios.delete(this.serverBaseURL + '/api/v1/users/logout')
        .then((_) => {
          router.push('/login')
        })
        .catch((_) => {
        })
    }
  },
  created () {
    if (this.$cookies.isKey('role')) {
      if (this.$cookies.get('role') === 'role=0') {
        this.showUserManagementModule = true
      } else {
        this.showUserManagementModule = false
      }
    } else {
      this.showUserManagementModule = false
    }

    if (this.$cookies.isKey('username')) {
      this.username = this.$cookies.get('username').split('=')[1]
    }
  }
}
</script>
