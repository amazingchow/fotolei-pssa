<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-12">
        <h1>商品明细库</h1>
        <hr>
        <alert :message=message v-if="showMessage"></alert>
        <div id="import-and-export-btn-area">
          <button type="button" class="btn btn-success btn-sm" v-b-modal.product-csv-file-modal>导入商品数据</button>
          <button type="button" class="btn btn-success btn-sm" v-b-modal.jit-inventory-csv-file-modal>导入即时库存</button>
        </div>
        <br/>
        <b-table-simple striped hover small id="product-table">
          <b-thead>
            <b-tr>
              <b-th scope="col">商品编号</b-th>
              <b-th scope="col">规格编号</b-th>
              <b-th scope="col">商品名称</b-th>
              <b-th scope="col">规格名称</b-th>
              <b-th scope="col">品牌</b-th>
              <b-th scope="col">分类1</b-th>
              <b-th scope="col">分类2</b-th>
              <b-th scope="col">产品系列</b-th>
              <b-th scope="col">STOP状态?</b-th>
              <b-th scope="col">重量/g</b-th>
              <b-th scope="col">长度/cm</b-th>
              <b-th scope="col">宽度/cm</b-th>
              <b-th scope="col">高度/cm</b-th>
              <b-th scope="col">组合商品?</b-th>
              <b-th scope="col">参与统计?</b-th>
              <b-th scope="col">进口商品?</b-th>
              <b-th scope="col">供应商名称</b-th>
              <b-th scope="col">采购名称</b-th>
              <b-th scope="col">即时库存</b-th>
            </b-tr>
          </b-thead>
          <b-tbody>
            <b-tr v-for="(product, index) in products" :key="index">
              <b-td>{{ product[0] }}</b-td>
              <b-td>{{ product[1] }}</b-td>
              <b-td>{{ product[2] }}</b-td>
              <b-td>{{ product[3] }}</b-td>
              <b-td>{{ product[4] }}</b-td>
              <b-td>{{ product[5] }}</b-td>
              <b-td>{{ product[6] }}</b-td>
              <b-td>{{ product[7] }}</b-td>
              <b-td>{{ product[8] }}</b-td>
              <b-td>{{ product[9] }}</b-td>
              <b-td>{{ product[10] }}</b-td>
              <b-td>{{ product[11] }}</b-td>
              <b-td>{{ product[12] }}</b-td>
              <b-td>{{ product[13] }}</b-td>
              <b-td>{{ product[14] }}</b-td>
              <b-td>{{ product[15] }}</b-td>
              <b-td>{{ product[16] }}</b-td>
              <b-td>{{ product[17] }}</b-td>
              <b-td>{{ product[18] }}</b-td>
            </b-tr>
          </b-tbody>
          <b-tfoot id="product-table-footer">
            <b-tr>
              <b-td colspan="19" variant="secondary">总共录入<b>{{ productsTotal }}</b>条记录, 当前展示<b>20</b>条记录</b-td>
            </b-tr>
          </b-tfoot>
        </b-table-simple>
        <div id="pagination-btn-area">
          <button class="btn btn-success btn-sm" :disabled="pageOffset==0" v-on:click="onPrevPage">前一页</button>
          <button class="btn btn-success btn-sm" :disabled="pageOffset==pageOffsetMax" v-on:click="onNextPage">后一页</button>
        </div>
      </div>
    </div>
    <b-modal ref="importProductCSVFileModal" id="product-csv-file-modal" title="导入商品数据" hide-footer>
      <b-form @submit="onImportProduct" @reset="onCancelImportProduct">
        <b-form-group>
          <b-form-file
            accept=".csv"
            v-model="importProductCSVFileForm.file"
            :state="Boolean(importProductCSVFileForm.file)"
            placeholder="请选择UTF-8编码的CSV文件">
          </b-form-file>
        </b-form-group>
        <br/>
        <b-button-group id="product-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导入</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
    <b-modal ref="importJITInventoryCSVFileModal" id="jit-inventory-csv-file-modal" title="导入即时库存" hide-footer>
      <b-form @submit="onImportJITInventory" @reset="onCancelImportJITInventory">
        <b-form-group>
          <b-form-file
            accept=".csv"
            v-model="importJITInventoryCSVFileForm.file"
            :state="Boolean(importJITInventoryCSVFileForm.file)"
            placeholder="请选择UTF-8编码的CSV文件">
          </b-form-file>
        </b-form-group>
        <br/>
        <b-button-group id="product-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导入</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
    <b-sidebar id="added-skus-sidebar" title="新增SKU清单" v-model="shouldOpenSidebar" right shadow>
      <div class="px-3 py-2">
        <b-table-simple striped hover small id="added-skus-table">
          <b-tbody>
            <b-tr v-for="(sku, index) in addedSkus" :key="index">
              <b-td>{{ sku }}</b-td>
            </b-tr>
          </b-tbody>
        </b-table-simple>
        <b-button-group id="added-skus-table-operate-btn" class="w-100 d-block">
          <b-button variant="dark" @click="onDownloadAddedSKUs">下载</b-button>
          <b-button variant="dark" @click="onCancelDownloadAddedSKUs">取消</b-button>
        </b-button-group>
      </div>
    </b-sidebar>
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

#added-skus-table {
  border: 2px solid black !important;
  font-size: small;
  table-layout: fixed !important;
}

#added-skus-table tbody tr td {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

#pagination-btn-area {
  text-align: center;
}

#product-table-operate-btn {
  text-align: right;
}

#added-skus-table-operate-btn {
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
      productsTotal: 0,
      shouldOpenSidebar: false,
      addedSkus: [],
      pageOffset: 0,
      pageOffsetMax: 0,
      importProductCSVFileForm: {
        file: null
      },
      importJITInventoryCSVFileForm: {
        file: null
      },
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
          this.productsTotal = parseInt(res.data.products_total)
          this.pageOffsetMax = this.productsTotal - this.productsTotal % 20
          console.log(this.pageOffsetMax)
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误!'
          this.showMessage = true
        })
    },
    importProductCSVFile (payload) {
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
    importJITInventoryCSVFile (payload) {
      axios.post('http://localhost:5000/api/v1/jitinventory/import', payload)
        .then((res) => {
          if (res.data.added_skus.length > 0) {
            this.message = '导入成功，同时有新增SKU'
            this.showMessage = true
            this.addedSkus = res.data.added_skus
            this.shouldOpenSidebar = true
          } else {
            this.listProducts()
            this.message = '导入成功!'
            this.showMessage = true
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '导入失败!'
          this.showMessage = true
        })
    },
    downloadAddedSKUs (payload) {
      axios.post('http://localhost:5000/api/v1/addedskus/download', payload)
        .then((res) => {
          this.message = '下载成功! 保存在' + res.data.output_file + '.'
          this.showMessage = true
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '下载失败!'
          this.showMessage = true
        })
    },
    initImportForm () {
      this.importProductCSVFileForm.file = null
      this.importJITInventoryCSVFileForm.file = null
    },
    onImportProduct (evt) {
      evt.preventDefault()
      this.$refs.importProductCSVFileModal.hide()
      const payload = {
        file: this.importProductCSVFileForm.file.name
      }
      this.importProductCSVFile(payload)
      this.initImportForm()
    },
    onCancelImportProduct (evt) {
      evt.preventDefault()
      this.$refs.importProductCSVFileModal.hide()
      this.initImportForm()
    },
    onImportJITInventory (evt) {
      evt.preventDefault()
      this.$refs.importJITInventoryCSVFileModal.hide()
      const payload = {
        file: this.importJITInventoryCSVFileForm.file.name
      }
      this.importJITInventoryCSVFile(payload)
      this.initImportForm()
    },
    onCancelImportJITInventory (evt) {
      evt.preventDefault()
      this.$refs.importJITInventoryCSVFileModal.hide()
      this.initImportForm()
    },
    onDownloadAddedSKUs (evt) {
      evt.preventDefault()
      const payload = {
        added_skus: this.addedSkus
      }
      this.downloadAddedSKUs(payload)
      this.shouldOpenSidebar = false
      this.addedSkus = []
    },
    onCancelDownloadAddedSKUs (evt) {
      evt.preventDefault()
      this.shouldOpenSidebar = false
      this.addedSkus = []
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
