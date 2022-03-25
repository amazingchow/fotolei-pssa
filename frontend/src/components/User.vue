<template>
  <div class="container-fluid" v-if="showUserManagementModule">
    <div class="row">
      <div class="col-sm-12">
        <b-navbar type="dark" variant="dark">
          <b-navbar-nav>
            <b-nav-item :active="false" href="/product">商品明细库</b-nav-item>
            <b-nav-item :active="false" href="/">库存明细库</b-nav-item>
            <b-nav-item :active="false" href="/slist">辅助查询</b-nav-item>
            <b-nav-item :active="false" href="/oplog">操作日志</b-nav-item>
            <b-nav-item :active="true" href="/user">用户管理</b-nav-item>
          </b-navbar-nav>
        </b-navbar>
      </div>
    </div>
    <br/>
    <div class="row">
      <div class="col-sm-3">
      </div>
      <div class="col-sm-6">
        <b-card bg-variant="light">
          <b-table-simple striped hover small id="users-table">
            <b-thead>
              <b-tr>
                <b-th scope="col">用户名</b-th>
                <b-th scope="col">用户角色</b-th>
              </b-tr>
            </b-thead>
            <b-tbody>
              <b-tr v-for="(user, index) in users" :key="index">
                <b-td>{{ user.username }}</b-td>
                <b-td v-if="user.role === 0">超级管理员</b-td>
                <b-td v-else-if="user.role === 1">普通管理员</b-td>
                <b-td v-else-if="user.role === 2">普通用户</b-td>
                <b-td v-else>匿名用户</b-td>
              </b-tr>
            </b-tbody>
          </b-table-simple>
          <div id="manage-user-btn-area">
            <button type="button" class="btn btn-secondary btn-sm" v-b-modal.create-user-modal>注册用户</button>
            <button type="button" class="btn btn-secondary btn-sm" v-b-modal.delete-user-modal>注销用户</button>
          </div>
        </b-card>
        <b-modal ref="createUserModal" id="create-user-modal" title="创建用户" hide-footer>
          <b-form>
            <b-card bg-variant="light">
              <b-form-group
                label="用户账号"
                label-size="sm"
                label-align-sm="right"
                label-cols-sm="3"
              >
                <b-form-input v-model="usernameOfCreatedUser" placeholder="只能为数字、大小写字母的组合" class="create-user-input"></b-form-input>
              </b-form-group>
              <b-form-group
                label="用户密码"
                label-size="sm"
                label-align-sm="right"
                label-cols-sm="3"
              >
                <b-form-input v-model="edDateSelection" placeholder="长度不能少于8位" class="create-user-input"></b-form-input>
              </b-form-group>
              <b-form-group
                label="用户权限"
                label-size="sm"
                label-align-sm="right"
                label-cols-sm="3"
              >
                <b-form-radio-group
                  v-model="roleTypeOfCreatedUser"
                  stacked
                >
                  <b-form-radio value=0>超级管理员</b-form-radio>
                  <b-form-radio value=1>普通管理员</b-form-radio>
                  <b-form-radio value=2>普通用户</b-form-radio>
                </b-form-radio-group>
              </b-form-group>
              <div id="create-user-btn-area" class="w-100 d-block">
                <b-button variant="dark" @click="onCreateUser">注册</b-button>
                <b-button variant="dark" @click="onCancelCreateUser">取消</b-button>
              </div>
            </b-card>
          </b-form>
        </b-modal>
        <b-modal ref="deleteUserModal" id="delete-user-modal" title="创建用户" hide-footer>
          <b-form>
            <b-card bg-variant="light">
              <b-form-group
                label="用户账号"
                label-size="sm"
                label-align-sm="right"
                label-cols-sm="3"
              >
                <b-form-input v-model="usernameOfDeletedUser" placeholder="只能为数字、大小写字母的组合" class="delete-user-input"></b-form-input>
              </b-form-group>
              <div id="delete-user-btn-area" class="w-100 d-block">
                <b-button variant="dark" @click="onDeleteUser">注销</b-button>
                <b-button variant="dark" @click="onCancelDeleteUser">取消</b-button>
              </div>
            </b-card>
          </b-form>
        </b-modal>
      </div>
      <div class="col-sm-3">
      </div>
    </div>
  </div>
</template>

<style>
#users-table {
  border: 2px solid black !important;
  font-size: small;
  table-layout: fixed !important;
}

#manage-user-btn-area {
  text-align: right;
}

.create-user-input {
  max-width: 300px;
}

#create-user-btn-area {
  text-align: right;
}

.delete-user-input {
  max-width: 300px;
}

#delete-user-btn-area {
  text-align: right;
}
</style>

<script>
import axios from 'axios'
import router from '../router'

export default {
  data () {
    return {
      serverBaseURL: process.env.SERVER_BASE_URL,

      users: [],
      usernameOfCreatedUser: '',
      passwordOfCreatedUser: '',
      roleTypeOfCreatedUser: 2,
      usernameOfDeletedUser: '',

      message: '',
      showMessage: false,
      showUserManagementModule: false
    }
  },
  methods: {
    async listUsers () {
      await axios.get(this.serverBaseURL + '/api/v1/users/?page.offset=0&page.limit=20')
        .then((res) => {
          const users = Object.freeze(res.data.users)
          this.users = users
        })
        .catch((error) => {
          if (error.response.status === 401) {
            router.push('/login')
          } else if (error.response.status === 403) {
            router.push('/404')
          } else {
            router.push('/500')
            // eslint-disable-next-line
            console.log(error)
            this.message = '内部服务错误！'
            this.showMessage = true
          }
        })
    }
  },
  created () {
    console.log(process.env.NODE_ENV)
    console.log(process.env.SERVER_BASE_URL)

    if (this.$cookies.isKey('role')) {
      if (this.$cookies.get('role') === 'role=0') {
        this.showUserManagementModule = true
        this.listUsers()
      } else {
        this.showUserManagementModule = false
        router.push('/404')
      }
    } else {
      this.showUserManagementModule = false
      router.push('/login')
    }
  }
}
</script>
