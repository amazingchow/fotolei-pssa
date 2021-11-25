<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-12">
        <h1>商品明细库</h1>
        <hr>
        <alert :message=message v-if="showMessage"></alert>
        <div id="input-btn-area">
          <button type="button" class="btn btn-success btn-sm" v-b-modal.csv-file-modal>导入库存数据报表</button>
        </div>
        <br/>
        <b-table-simple striped hover small id="inventory-table">
          <b-thead>
            <b-tr>
              <b-th scope="col">商品编号</b-th>
              <b-th scope="col">商品名称</b-th>
              <b-th scope="col">规格编号</b-th>
              <b-th scope="col">品牌</b-th>
              <b-th scope="col">分类一</b-th>
              <b-th scope="col">分类二</b-th>
              <b-th scope="col">商品系列</b-th>
              <b-th scope="col">STOP状态?</b-th>
              <b-th scope="col">商品重量/g</b-th>
              <b-th scope="col">商品长度/cm</b-th>
              <b-th scope="col">商品宽度/cm</b-th>
              <b-th scope="col">商品高度/cm</b-th>
              <b-th scope="col">组合商品?</b-th>
              <b-th scope="col">参与统计?</b-th>
              <b-th scope="col">进口商品?</b-th>
              <b-th scope="col">供应商编号</b-th>
              <b-th scope="col">采购名称</b-th>
              <b-th scope="col">录入时间</b-th>
            </b-tr>
          </b-thead>
          <b-tbody>
            <b-tr v-for="(inventory, index) in inventories" :key="index">
              <b-td>{{ inventory[0] }}</b-td>
              <b-td>{{ inventory[1] }}</b-td>
              <b-td>{{ inventory[2] }}</b-td>
              <b-td>{{ inventory[3] }}</b-td>
              <b-td>{{ inventory[4] }}</b-td>
              <b-td>{{ inventory[5] }}</b-td>
              <b-td>{{ inventory[6] }}</b-td>
              <b-td>{{ inventory[7] }}</b-td>
              <b-td>{{ inventory[8] }}</b-td>
              <b-td>{{ inventory[9] }}</b-td>
              <b-td>{{ inventory[10] }}</b-td>
              <b-td>{{ inventory[11] }}</b-td>
              <b-td>{{ inventory[12] }}</b-td>
              <b-td>{{ inventory[13] }}</b-td>
              <b-td>{{ inventory[14] }}</b-td>
              <b-td>{{ inventory[15] }}</b-td>
              <b-td>{{ inventory[16] }}</b-td>
              <b-td>{{ inventory[17] }}</b-td>
            </b-tr>
          </b-tbody>
          <b-tfoot id="inventory-table-footer">
            <b-tr>
              <b-td colspan="18" variant="secondary">总共录入<b>{{ inventories_total }}</b>条记录, 当前展示<b>20</b>条记录</b-td>
            </b-tr>
          </b-tfoot>
        </b-table-simple>
        <div id="pagination-btn-area">
          <button class="btn btn-success btn-sm" :disabled="pageOffset==0" v-on:click="onPrevPage">前一页</button>
          <button class="btn btn-success btn-sm" v-on:click="onNextPage">后一页</button>
        </div>
      </div>
    </div>
    <b-modal ref="loadCSVFileModal" id="csv-file-modal" title="导入库存数据报表" hide-footer>
      <b-form @submit="onSubmit" @reset="onReset">
        <b-form-group id="form-csv-file-group" label-for="form-csv-file-input">
            <b-form-input id="form-csv-file-input" type="text" v-model="loadCSVFileForm.file" required placeholder="请选择UTF-8编码的CSV文件"></b-form-input>
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

#inventory-table-footer {
  text-align: right;
}

#input-btn-area {
  text-align: right;
}

#pagination-btn-area {
  text-align: center;
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
      inventories_total: '0',
      loadCSVFileForm: {
        file: ''
      },
      pageOffset: 0,
      message: '',
      showMessage: false
    }
  },
  components: {
    alert: Alert
  },
  methods: {
    listInventories () {
      axios.get(`http://localhost:5000/api/v1/inventories?page.offset=${this.pageOffset}&page.limit=20`)
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
    getInventoriesTotal () {
      axios.get('http://localhost:5000/api/v1/inventories/total')
        .then((res) => {
          this.inventories_total = res.data.inventories_total
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
          this.getInventoriesTotal()
          this.message = '导入成功!'
          this.showMessage = true
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
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
    },
    onPrevPage (evt) {
      evt.preventDefault()
      this.pageOffset -= 20
      this.listInventories()
    },
    onNextPage (evt) {
      evt.preventDefault()
      this.pageOffset += 20
      this.listInventories()
    }
  },
  created () {
    this.listInventories()
    this.getInventoriesTotal()
  }
}
</script>
