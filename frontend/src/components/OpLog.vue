<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-3">
      </div>
      <div class="col-sm-6">
        <b-card bg-variant="light">
          <b-table-simple striped hover small id="inventory-table">
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
#inventory-table {
  border: 2px solid black !important;
  font-size: small;
  table-layout: fixed !important;
}
</style>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      serverBaseURL: process.env.SERVER_BASE_URL,
      oplogs: []
    }
  },
  methods: {
    getOpLogs () {
      axios.get(this.serverBaseURL + '/api/v1/oplogs')
        .then((res) => {
          this.oplogs = res.data.oplogs
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误!'
          this.showMessage = true
        })
    }
  },
  created () {
    console.log(process.env.NODE_ENV)
    console.log(process.env.SERVER_BASE_URL)
    this.getOpLogs()
  }
}
</script>
