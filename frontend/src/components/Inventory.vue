<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-12">
        <h1>商品明细库</h1>
        <hr>
        <alert :message=message v-if="showMessage"></alert>
        <button type="button" class="btn btn-success btn-sm" v-b-modal.csv-file-modal>导入进销存报表</button>
        <br/><br/>
        <table id="inventory-table" class="table table-sm w-100">
          <thead>
            <tr>
              <th scope="col">商品编号</th>
              <th scope="col">商品名称</th>
              <th scope="col">规格编号</th>
              <th scope="col">品牌</th>
              <th scope="col">分类一</th>
              <th scope="col">分类二</th>
              <th scope="col">商品系列</th>
              <th scope="col">STOP状态?</th>
              <th scope="col">商品重量/g</th>
              <th scope="col">商品长度/cm</th>
              <th scope="col">商品宽度/cm</th>
              <th scope="col">商品高度/cm</th>
              <th scope="col">组合商品?</th>
              <th scope="col">参与统计?</th>
              <th scope="col">进口商品?</th>
              <th scope="col">供应商编号</th>
              <th scope="col">采购名称</th>
              <th scope="col">录入时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(inventory, index) in inventories" :key="index">
              <td>{{ inventory[1] }}</td>
              <td>{{ inventory[2] }}</td>
              <td>{{ inventory[3] }}</td>
              <td>{{ inventory[4] }}</td>
              <td>{{ inventory[5] }}</td>
              <td>{{ inventory[6] }}</td>
              <td>{{ inventory[7] }}</td>
              <td>
                <span v-if="inventory[8] == 0">停用</span>
                <span v-else>在用</span>
              </td>
              <td>{{ inventory[9] }}</td>
              <td>{{ inventory[10] }}</td>
              <td>{{ inventory[11] }}</td>
              <td>
                <span v-if="inventory[12] == 0">否</span>
                <span v-else>是</span>
              </td>
              <td>
                <span v-if="inventory[13] == 0">不参与</span>
                <span v-else>参与</span>
              </td>
              <td>
                <span v-if="inventory[14] == 0">非进口品</span>
                <span v-else>进口品</span>
              </td>
              <td>{{ inventory[15] }}</td>
              <td>{{ inventory[16] }}</td>
              <td>{{ inventory[17] }}</td>
              <td>{{ inventory[19] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <b-modal ref="loadCSVFileModal" id="csv-file-modal" title="导入进销存报表" hide-footer>
      <b-form @submit="onSubmit" @reset="onReset" class="w-100 d-block">
        <b-form-group id="form-csv-file-group" label-for="form-csv-file-input">
            <b-form-input id="form-csv-file-input" type="text" v-model="loadCSVFileForm.title" required placeholder="请选择UTF-8编码的CSV文件"></b-form-input>
        </b-form-group>
        <br/>
        <b-button-group id="inventory-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导入</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
  </div>
</template>

<style>
#inventory-table {
  font-size: small;
  table-layout: fixed !important;
}

#inventory-table tbody tr td {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

#inventory-table-operate-btn {
  text-align: right;
}
</style>

<script>
import axios from 'axios'
import Alert from './Alert.vue'

export default {
  data () {
    return {
      inventories: [],
      loadCSVFileForm: {
        file: ''
      },
      message: '',
      showMessage: false
    }
  },
  components: {
    alert: Alert
  },
  methods: {
    listInventories () {
      axios.get('http://localhost:5000/api/v1/inventories?page.offset=0&page.limit=20')
        .then((res) => {
          this.inventories = res.data.inventories
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误!'
          this.showMessage = true
        })
    },
    loadCSVFile (payload) {
      axios.post('http://localhost:5000/api/v1/input', payload)
        .then(() => {
          this.listInventories()
          this.message = '导入成功!'
          this.showMessage = true
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.listInventories()
          this.message = '导入失败!'
          this.showMessage = true
        })
    },
    initForm () {
      this.loadCSVFileForm.file = ''
    },
    onSubmit (evt) {
      evt.preventDefault()
      this.$refs.loadCSVFileModal.hide()
      const payload = {
        file: this.loadCSVFileForm.file
      }
      this.loadCSVFile(payload)
      this.initForm()
    },
    onReset (evt) {
      evt.preventDefault()
      this.$refs.loadCSVFileModal.hide()
      this.initForm()
    }
  },
  created () {
    this.listInventories()
  }
}
</script>
