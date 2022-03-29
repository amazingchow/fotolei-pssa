<template>
  <div class="container-fluid" v-if="showUserManagementPage">
    <navbar></navbar>
    <br/>
    <alert :message=message v-if="showMessage"></alert>
    <div class="row">
      <div class="col-sm-3">
      </div>
      <div class="col-sm-6">
        <b-list-group>
          <b-list-group-item>
            <b-badge variant="secondary">超级管理员</b-badge>
            <br/>
            <b-badge variant="light">* 注册/注销用户（无法注销超级管理员fotolei）</b-badge>
            <br/>
            <b-badge variant="light">* 导入/查看/修改/删除/导出数据（包括产品数据和进销存数据）</b-badge>
          </b-list-group-item>
          <b-list-group-item>
            <b-badge variant="secondary">普通管理员</b-badge>
            <br/>
            <b-badge variant="light">* 查看/导出数据（包括产品数据和进销存数据）</b-badge>
          </b-list-group-item>
          <b-list-group-item>
            <b-badge variant="secondary">普通用户</b-badge>
            <br/>
            <b-badge variant="light">* 查看/导出数据（包括产品数据和进销存数据，但涉及敏感金额的地方，不予展示）</b-badge>
          </b-list-group-item>
        </b-list-group>
        <br>
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
                <b-form-input v-model="passwordOfCreatedUser" placeholder="长度不能少于8位" class="create-user-input"></b-form-input>
              </b-form-group>
              <b-form-group
                label="用户权限"
                label-size="sm"
                label-align-sm="right"
                label-cols-sm="3"
              >
                <b-form-radio-group
                  stacked
                >
                  <b-form-radio v-model="roleTypeOfCreatedUser" value=0>超级管理员</b-form-radio>
                  <b-form-radio v-model="roleTypeOfCreatedUser" value=1>普通管理员</b-form-radio>
                  <b-form-radio v-model="roleTypeOfCreatedUser" value=2>普通用户</b-form-radio>
                </b-form-radio-group>
              </b-form-group>
              <div id="create-user-btn-area" class="w-100 d-block">
                <b-button variant="dark" @click="onCreateUser">注册</b-button>
                <b-button variant="dark" @click="onCancelCreateUser">取消</b-button>
              </div>
            </b-card>
          </b-form>
        </b-modal>
        <b-modal ref="deleteUserModal" id="delete-user-modal" title="删除用户" hide-footer>
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
import Alert from './Alert.vue'
import Navbar from './Navbar.vue'
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
      showUserManagementPage: false
    }
  },
  components: {
    alert: Alert,
    navbar: Navbar
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
            // eslint-disable-next-line
            console.log(error)
            router.push('/500')
          }
        })
    },
    onCreateUser (evt) {
      evt.preventDefault()
      this.$refs.createUserModal.hide()
      const payload = {
        username: this.usernameOfCreatedUser,
        password: this.passwordOfCreatedUser,
        role: this.roleTypeOfCreatedUser
      }
      this.createUser(payload)
      this.usernameOfCreatedUser = ''
      this.passwordOfCreatedUser = ''
      this.roleTypeOfCreatedUser = 2
    },
    onCancelCreateUser (evt) {
      evt.preventDefault()
      this.$refs.createUserModal.hide()
      this.usernameOfCreatedUser = ''
      this.passwordOfCreatedUser = ''
      this.roleTypeOfCreatedUser = 2
    },
    async createUser (payload) {
      await axios.post(this.serverBaseURL + '/api/v1/users/register', payload)
        .then((_) => {
          this.listUsers()
        })
        .catch((error) => {
          if (error.response.status === 401) {
            router.push('/login')
          } else if (error.response.status === 403) {
            router.push('/404')
          } else {
            // eslint-disable-next-line
            console.log(error)
            router.push('/500')
          }
        })
    },
    onDeleteUser (evt) {
      evt.preventDefault()
      this.$refs.deleteUserModal.hide()
      if (this.usernameOfDeletedUser === 'fotolei') {
        this.message = '禁止注销超级管理员fotolei！'
        this.showMessage = true
      } else {
        this.deleteUser(this.usernameOfDeletedUser)
      }
      this.usernameOfDeletedUser = ''
    },
    onCancelDeleteUser (evt) {
      evt.preventDefault()
      this.$refs.deleteUserModal.hide()
      this.usernameOfDeletedUser = ''
    },
    async deleteUser (username) {
      await axios.delete(this.serverBaseURL + '/api/v1/users/unregister?username=' + username)
        .then((_) => {
          this.listUsers()
        })
        .catch((error) => {
          if (error.response.status === 401) {
            router.push('/login')
          } else if (error.response.status === 403) {
            router.push('/404')
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

    if (this.$cookies.isKey('role')) {
      if (this.$cookies.get('role') === '0') {
        this.showUserManagementPage = true
        this.listUsers()
      } else {
        this.showUserManagementPage = false
        router.push('/404')
      }
    } else {
      this.showUserManagementPage = false
      router.push('/login')
    }
  }
}
</script>
