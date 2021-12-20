<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-12">
        <alert :message=message v-if="showMessage"></alert>
        <div id="import-and-export-btn-area">
          <button type="button" class="btn btn-success btn-sm" v-b-modal.product-csv-file-modal>导入商品明细</button>
          <button type="button" class="btn btn-success btn-sm" v-b-modal.jit-inventory-csv-file-modal>导入即时库存</button>
          <button type="button" class="btn btn-success btn-sm" v-b-modal.products-clean-all-modal>删除商品明细</button>
        </div>
        <br/>
        <b-table-simple striped hover small id="product-table">
          <b-thead>
            <b-tr>
              <b-th scope="col">商品编码</b-th>
              <b-th scope="col">规格编码</b-th>
              <b-th scope="col">商品名称</b-th>
              <b-th scope="col">规格名称</b-th>
              <b-th scope="col">品牌</b-th>
              <b-th scope="col">分类1</b-th>
              <b-th scope="col">分类2</b-th>
              <b-th scope="col">产品系列</b-th>
              <b-th scope="col">STOP状态?</b-th>
              <b-th scope="col">组合商品?</b-th>
              <b-th scope="col">进口商品?</b-th>
              <b-th scope="col">供应商名称</b-th>
              <b-th scope="col">采购名称</b-th>
              <b-th scope="col">实时可用库存</b-th>
              <b-th scope="col">MOQ</b-th>
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
            </b-tr>
          </b-tbody>
          <b-tfoot id="product-table-footer">
            <b-tr>
              <b-td colspan="15" variant="secondary">总共录入<b>{{ productsTotal }}</b>条记录，共计<b>{{ pageTotal }}</b>页，当前展示第<b>{{ pageCurr }}</b>页，共<b>{{ productsNum }}</b>条记录</b-td>
            </b-tr>
          </b-tfoot>
        </b-table-simple>
        <div id="pagination-btn-area">
          <button class="btn btn-success btn-sm" v-on:click="onFirstPage">首页</button>
          <button class="btn btn-success btn-sm" :disabled="pageOffset==0" v-on:click="onPrevPage">前一页</button>
          <input v-model="pageJump" type="number" placeholder="1" style="width: 10ch;" />
          <button class="btn btn-success btn-sm" v-on:click="onJumpPage">快捷跳转</button>
          <button class="btn btn-success btn-sm" :disabled="pageOffset==pageOffsetMax" v-on:click="onNextPage">后一页</button>
          <button class="btn btn-success btn-sm" v-on:click="onLastPage">尾页</button>
        </div>
      </div>
    </div>
    <b-modal ref="importProductCSVFileModal" id="product-csv-file-modal" title="导入商品明细数据" hide-footer>
      <b-form @submit="onImportProducts" @reset="onCancelImportProducts">
        <b-form-group>
          <b-form-file
            accept=".csv"
            v-model="uploadProductCSVFile"
            :state="Boolean(uploadProductCSVFile)"
            placeholder="请选择UTF-8编码的CSV文件">
          </b-form-file>
        </b-form-group>
        <br/>
        <div id="product-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导入</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </div>
      </b-form>
    </b-modal>
    <b-modal ref="importJITInventoryCSVFileModal" id="jit-inventory-csv-file-modal" title="导入即时库存" hide-footer>
      <b-form @submit="onImportJITInventory" @reset="onCancelImportJITInventory">
        <b-form-group>
          <b-form-file
            accept=".csv"
            v-model="uploadJITInventoryCSVFile"
            :state="Boolean(uploadJITInventoryCSVFile)"
            placeholder="请选择UTF-8编码的CSV文件">
          </b-form-file>
        </b-form-group>
        <br/>
        <div id="product-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导入</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </div>
      </b-form>
    </b-modal>
    <b-modal ref="CleanAllProductsModal" id="products-clean-all-modal" title="删除全量商品明细" hide-footer>
      <b-form @submit="onCleanAllProducts" @reset="onCancelCleanAllProducts">
        <b-form-group
          label="管理员账号"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="adminUsr"></b-form-input>
        </b-form-group>
        <b-form-group
          label="管理员密码"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="adminPwd" type="password"></b-form-input>
        </b-form-group>
        <br/>
        <div id="product-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">删除</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </div>
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
        <div id="added-skus-table-operate-btn" class="w-100 d-block">
          <b-button variant="dark" @click="onDownloadAddedSKUs">下载</b-button>
          <b-button variant="dark" @click="onCancelDownloadAddedSKUs">取消</b-button>
        </div>
      </div>
    </b-sidebar>
  </div>
</template>

<style>
#product-table {
  border: 2px solid black !important;
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
      serverBaseURL: process.env.SERVER_BASE_URL,
      products: [],
      productsNum: 0,
      productsTotal: 0,
      shouldOpenSidebar: false,
      addedSkus: [],
      pageJump: 1,
      pageCurr: 0,
      pageTotal: 0,
      pageOffset: 0,
      pageOffsetMax: 0,
      uploadProductCSVFile: null,
      uploadJITInventoryCSVFile: null,
      adminUsr: '',
      adminPwd: '',
      message: '',
      showMessage: false
    }
  },
  components: {
    alert: Alert
  },
  methods: {
    listProducts () {
      axios.get(this.serverBaseURL + `/api/v1/products?page.offset=${this.pageOffset}&page.limit=20`)
        .then((res) => {
          this.products = res.data.products
          this.productsNum = res.data.products.length
          if (this.productsNum > 0) {
            this.pageCurr = this.pageOffset / 20 + 1
          } else {
            this.pageCurr = 0
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误!'
          this.showMessage = true
        })
    },
    getProductsTotal () {
      axios.get(this.serverBaseURL + '/api/v1/products/total')
        .then((res) => {
          this.productsTotal = res.data.products_total
          this.pageOffsetMax = this.productsTotal - this.productsTotal % 20
          if (this.productsTotal > 0) {
            this.pageTotal = this.pageOffsetMax / 20 + 1
          } else {
            this.pageTotal = 0
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误!'
          this.showMessage = true
        })
    },
    importProductCSVFile (formData) {
      let config = {
        header: {
          'Content-Type': 'multipart/form-data'
        }
      }
      axios.post(this.serverBaseURL + '/api/v1/products/upload', formData, config)
        .then((res) => {
          if (res.data.status === 'success') {
            this.message = '导入成功！预计导入' + res.data.items_total.toString() + '条，实际导入' + res.data.items_add.toString() + '条，去重' + res.data.items_exist.toString() + '条。'
            this.showMessage = true
            if (res.data.items_add > 0) {
              this.listProducts()
              this.getProductsTotal()
            }
          } else if (res.data.status === 'invalid input data schema') {
            this.message = '导入失败！数据表格格式有变更，请人工复核！'
            this.showMessage = true
          } else if (res.data.status === 'repetition') {
            this.message = '导入失败！数据表格重复导入！'
            this.showMessage = true
          } else if (res.data.status === 'invalid input data') {
            this.message = '导入失败！' + res.data.err_msg
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
    importJITInventoryCSVFile (formData) {
      let config = {
        header: {
          'Content-Type': 'multipart/form-data'
        }
      }
      axios.post(this.serverBaseURL + '/api/v1/jitinventory/upload', formData, config)
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
    cleanAllProducts (payload) {
      axios.post(this.serverBaseURL + '/api/v1/products/clean', payload)
        .then((res) => {
          if (res.data.status === 'success') {
            this.message = '删除成功！'
            this.showMessage = true
          } else if (res.data.status === 'invalid input data') {
            this.message = '删除失败，管理员账号或密码错误！'
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
    preDownloadAddedSKUs (payload) {
      axios.post(this.serverBaseURL + '/api/v1/addedskus/prepare', payload)
        .then((res) => {
          this.downloadAddedSKUs(res.data.server_send_queue_file, res.data.output_file)
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '下载失败!'
          this.showMessage = true
        })
    },
    downloadAddedSKUs (queryFile, saveFile) {
      axios.get(this.serverBaseURL + '/api/v1/download/' + queryFile)
        .then((res) => {
          const evt = document.createEvent('MouseEvents')
          var docUrl = document.createElement('a')
          docUrl.download = saveFile
          docUrl.href = window.URL.createObjectURL(new Blob([res.data]), {type: 'text/plain'})
          docUrl.dataset.downloadurl = ['.csv', docUrl.download, docUrl.href].join(':')
          // TODO: 替换为支持的解决方案
          evt.initEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null)
          docUrl.dispatchEvent(evt)
          this.message = '下载成功! 保存为本地文件<' + saveFile + '>.'
          this.showMessage = true
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '下载失败!'
          this.showMessage = true
        })
    },
    onImportProducts (evt) {
      evt.preventDefault()
      this.$refs.importProductCSVFileModal.hide()
      let formData = new FormData()
      formData.append('file', this.uploadProductCSVFile, this.uploadProductCSVFile.name)
      this.importProductCSVFile(formData)
      this.uploadProductCSVFile = null
    },
    onCancelImportProducts (evt) {
      evt.preventDefault()
      this.$refs.importProductCSVFileModal.hide()
      this.uploadProductCSVFile = null
    },
    onImportJITInventory (evt) {
      evt.preventDefault()
      this.$refs.importJITInventoryCSVFileModal.hide()
      let formData = new FormData()
      formData.append('file', this.uploadJITInventoryCSVFile, this.uploadJITInventoryCSVFile.name)
      this.importJITInventoryCSVFile(formData)
      this.uploadJITInventoryCSVFile = null
    },
    onCancelImportJITInventory (evt) {
      evt.preventDefault()
      this.$refs.importJITInventoryCSVFileModal.hide()
      this.uploadJITInventoryCSVFile = null
    },
    onCleanAllProducts (evt) {
      evt.preventDefault()
      this.$refs.CleanAllProductsModal.hide()
      const payload = {
        admin_usr: this.adminUsr,
        admin_pwd: this.adminPwd
      }
      this.cleanAllProducts(payload)
      this.products = []
      this.productsNum = 0
      this.productsTotal = 0
      this.pageJump = 1
      this.pageCurr = 0
      this.pageTotal = 0
      this.pageOffset = 0
      this.pageOffsetMax = 0
      this.adminUsr = ''
      this.adminPwd = ''
    },
    onCancelCleanAllProducts (evt) {
      evt.preventDefault()
      this.$refs.CleanAllProductsModal.hide()
      this.adminUsr = ''
      this.adminPwd = ''
    },
    onDownloadAddedSKUs (evt) {
      evt.preventDefault()
      const payload = {
        added_skus: this.addedSkus
      }
      this.preDownloadAddedSKUs(payload)
      this.shouldOpenSidebar = false
      this.addedSkus = []
    },
    onCancelDownloadAddedSKUs (evt) {
      evt.preventDefault()
      this.shouldOpenSidebar = false
      this.addedSkus = []
    },
    onFirstPage (evt) {
      evt.preventDefault()
      this.pageOffset = 0
      this.listProducts()
    },
    onJumpPage (evt) {
      evt.preventDefault()
      if (this.pageJump <= 0 || this.pageJump > this.pageTotal) {
        this.pageOffset = 0
      } else {
        this.pageOffset = (this.pageJump - 1) * 20
      }
      this.listProducts()
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
    },
    onLastPage (evt) {
      evt.preventDefault()
      this.pageOffset = this.pageOffsetMax
      this.listProducts()
    }
  },
  created () {
    console.log(process.env.NODE_ENV)
    console.log(process.env.SERVER_BASE_URL)
    this.listProducts()
    this.getProductsTotal()
  }
}
</script>
