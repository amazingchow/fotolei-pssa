<template>
  <div class="container-fluid">
    <navbar></navbar>
    <br/>
    <alert :message=message v-if="showMessage"></alert>
    <div class="row">
      <div class="col-sm-3">
      </div>
      <div class="col-sm-6">
        <b-card bg-variant="light">
          <b-table-simple striped hover small id="oplogs-table">
            <b-thead>
              <b-tr>
                <b-th scope="col">操作时间</b-th>
                <b-th scope="col">操作日志</b-th>
              </b-tr>
            </b-thead>
            <b-tbody>
              <b-tr v-for="(oplog, index) in oplogs" :key="index">
                <b-td>{{ oplog.create_time }}</b-td>
                <b-td>{{ oplog.oplog }}</b-td>
              </b-tr>
            </b-tbody>
          </b-table-simple>
        </b-card>
      </div>
      <div class="col-sm-3">
      </div>
    </div>
  </div>
</template>

<style>
#oplogs-table {
  border: 2px solid black !important;
  font-size: small;
  table-layout: fixed !important;
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

      oplogs: [],

      message: '',
      showMessage: false
    }
  },
  components: {
    alert: Alert,
    navbar: Navbar
  },
  methods: {
    async listOpLogs () {
      await axios.get(this.serverBaseURL + '/api/v1/common/oplogs')
        .then((res) => {
          const oplogs = Object.freeze(res.data.oplogs)
          this.oplogs = oplogs
        })
        .catch((error) => {
          if (error.response.status === 401) {
            router.push('/login')
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

    if (this.$cookies.isKey('logged')) {
      if (this.$cookies.get('logged') === 'in') {
        this.listOpLogs()
      } else {
        router.push('/login')
      }
    } else {
      router.push('/login')
    }
  }
}
</script>
