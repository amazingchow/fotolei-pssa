<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-12">
        <h1>商品明细库</h1>
        <hr>
        <alert :message=message v-if="showMessage"></alert>
        <div id="import-and-export-btn-area">
          <button type="button" class="btn btn-success btn-sm" v-b-modal.csv-file-modal>导入商品数据</button>
        </div>
        <br/>
        <b-table-simple striped hover small id="product-table">
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
            </b-tr>
          </b-thead>
          <b-tbody>
            <b-tr v-for="(products, index) in products" :key="index">
              <b-td>{{ products[0] }}</b-td>
              <b-td>{{ products[1] }}</b-td>
              <b-td>{{ products[2] }}</b-td>
              <b-td>{{ products[3] }}</b-td>
              <b-td>{{ products[4] }}</b-td>
              <b-td>{{ products[5] }}</b-td>
              <b-td>{{ products[6] }}</b-td>
              <b-td>{{ products[7] }}</b-td>
              <b-td>{{ products[8] }}</b-td>
              <b-td>{{ products[9] }}</b-td>
              <b-td>{{ products[10] }}</b-td>
              <b-td>{{ products[11] }}</b-td>
              <b-td>{{ products[12] }}</b-td>
              <b-td>{{ products[13] }}</b-td>
              <b-td>{{ products[14] }}</b-td>
              <b-td>{{ products[15] }}</b-td>
              <b-td>{{ products[16] }}</b-td>
            </b-tr>
          </b-tbody>
          <b-tfoot id="product-table-footer">
            <b-tr>
              <b-td colspan="17" variant="secondary">总共录入<b>{{ products_total }}</b>条记录, 当前展示<b>20</b>条记录</b-td>
            </b-tr>
          </b-tfoot>
        </b-table-simple>
        <div id="pagination-btn-area">
          <button class="btn btn-success btn-sm" :disabled="pageOffset==0" v-on:click="onPrevPage">前一页</button>
          <button class="btn btn-success btn-sm" v-on:click="onNextPage">后一页</button>
        </div>
      </div>
    </div>
    <b-modal ref="importCSVFileModal" id="csv-file-modal" title="导入商品数据" hide-footer>
      <b-form @submit="onImport" @reset="onCancel">
        <b-form-group id="form-csv-file-group" label-for="form-csv-file-input">
            <b-form-input id="form-csv-file-input" type="text" v-model="importCSVFileForm.file" required placeholder="请选择UTF-8编码的CSV文件"></b-form-input>
        </b-form-group>
        <br/>
        <b-button-group id="product-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导入</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
  </div>
</template>

<style>
#product-table {
  font-size: small;
  table-layout: fixed !important;
}

#product-table tbody tr td {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

#product-table-footer {
  text-align: right;
}

#pagination-btn-area {
  text-align: center;
}

#product-table-operate-btn {
  text-align: right;
}
</style>

<script>
import axios from 'axios'
import Alert from './Alert.vue'

export default {
  data () {
    return {
      products: [],
      products_total: '0',
      importCSVFileForm: {
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
    listProducts () {
      axios.get(`http://localhost:5000/api/v1/products?page.offset=${this.pageOffset}&page.limit=20`)
        .then((res) => {
          this.products = res.data.products
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误!'
          this.showMessage = true
        })
    },
    getProductsTotal () {
      axios.get('http://localhost:5000/api/v1/products/total')
        .then((res) => {
          this.products_total = res.data.products_total
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误!'
          this.showMessage = true
        })
    },
    importCSVFile (payload) {
      axios.post('http://localhost:5000/api/v1/products/import', payload)
        .then(() => {
          this.listProducts()
          this.getProductsTotal()
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
    initInportForm () {
      this.importCSVFileForm.file = ''
    },
    onImport (evt) {
      evt.preventDefault()
      this.$refs.importCSVFileModal.hide()
      const payload = {
        file: this.importCSVFileForm.file
      }
      this.importCSVFile(payload)
      this.initInportForm()
    },
    onCancel (evt) {
      evt.preventDefault()
      this.$refs.importCSVFileModal.hide()
      this.initInportForm()
    },
    onPrevPage (evt) {
      evt.preventDefault()
      this.pageOffset -= 20
      this.listProducts()
    },
    onNextPage (evt) {
      evt.preventDefault()
      this.pageOffset += 20
      this.listProducts()
    }
  },
  created () {
    this.listProducts()
    this.getProductsTotal()
  }
}
</script>
