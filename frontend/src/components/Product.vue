<template>
  <div class="container-fluid">
    <navbar></navbar>
    <br/>
    <alert :message=message v-if="showMessage"></alert>
    <div class="row">
      <div class="col-sm-12">
        <div id="import-and-export-btn-area">
          <button type="button" class="btn btn-secondary btn-sm" v-b-modal.product-csv-file-modal>导入商品明细</button>
          <button type="button" class="btn btn-secondary btn-sm" v-b-modal.products-clean-all-modal>删除全量商品明细</button>
          <button type="button" class="btn btn-secondary btn-sm" v-b-modal.product-clean-one-modal>删除单条商品明细</button>
          <button type="button" class="btn btn-secondary btn-sm" v-b-modal.jit-inventory-csv-file-modal>导入即时库存</button>
          <button type="button" class="btn btn-secondary btn-sm" v-b-modal.unit-price-csv-file-modal>导入单价</button>
          <button type="button" class="btn btn-secondary btn-sm" v-b-modal.update-one-product-modal>更新商品明细</button>
        </div>
        <b-table-simple striped hover small id="product-table">
          <b-thead>
            <b-tr>
              <b-th scope="col">规格编码</b-th>
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
              <b-th scope="col">单价</b-th>
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
            </b-tr>
          </b-tbody>
          <b-tfoot id="product-table-footer">
            <b-tr>
              <b-td colspan="13" variant="secondary">总共录入<b>{{ productsTotal }}</b>条记录，共计<b>{{ pageTotal }}</b>页，当前展示第<b>{{ pageCurr }}</b>页，共<b>{{ productsNum }}</b>条记录</b-td>
            </b-tr>
          </b-tfoot>
        </b-table-simple>
        <div id="pagination-btn-area">
          <button class="btn btn-secondary btn-sm" v-on:click="onFirstPage">首页</button>
          <button class="btn btn-secondary btn-sm" :disabled="pageOffset==0" v-on:click="onPrevPage">前一页</button>
          <input v-model="pageJump" type="number" min="0" step="1" placeholder="1" style="width: 10ch;" />
          <button class="btn btn-secondary btn-sm" v-on:click="onJumpPage">快捷跳转</button>
          <button class="btn btn-secondary btn-sm" :disabled="pageOffset==pageOffsetMax" v-on:click="onNextPage">后一页</button>
          <button class="btn btn-secondary btn-sm" v-on:click="onLastPage">尾页</button>
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
    <b-modal ref="importUnitPriceCSVFileModal" id="unit-price-csv-file-modal" title="导入单价" hide-footer>
      <b-form @submit="onImportUnitPrice" @reset="onCancelImportUnitPrice">
        <b-form-group>
          <b-form-file
            accept=".csv"
            v-model="uploadUnitPriceCSVFile"
            :state="Boolean(uploadUnitPriceCSVFile)"
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
    <b-modal ref="CleanOneProductModal" id="product-clean-one-modal" title="删除单条商品明细" hide-footer>
      <b-form @submit="onCleanOneProduct" @reset="onCancelCleanOneProduct">
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
        <b-form-group
          label="规格编码"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="specificationCode"></b-form-input>
        </b-form-group>
        <br/>
        <div id="product-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">删除</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </div>
      </b-form>
    </b-modal>
    <b-modal ref="updateOneProductModal" id="update-one-product-modal" title="更新某一条商品明细" hide-footer>
      <b-form>
        <b-form-group
          label="规格编码"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.specificationCode"></b-form-input>
        </b-form-group>
        <b-form-text>提示1：通过规格编码加载已有商品条目，再按需修改条目</b-form-text>
        <b-form-text>提示2：不要直接修改规格编码，先删除该商品条目，再重新导入来更新规格编码</b-form-text>
        <hr/>
        <b-form-group
          label="商品编码"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.productCode"></b-form-input>
        </b-form-group>
        <b-form-group
          label="商品名称"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.productName"></b-form-input>
        </b-form-group>
        <b-form-group
          label="规格名称"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.specificationName"></b-form-input>
        </b-form-group>
        <b-form-group
          label="品牌"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.brand"></b-form-input>
        </b-form-group>
        <b-form-group
          label="分类1"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.classification1"></b-form-input>
        </b-form-group>
        <b-form-group
          label="分类2"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.classification2"></b-form-input>
        </b-form-group>
        <b-form-group
          label="产品系列"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.productSeries"></b-form-input>
        </b-form-group>
        <b-form-group
          label="STOP状态"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.stopStatus"></b-form-input>
        </b-form-group>
        <b-form-group
          label="重量/g"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.productWeight" type="number"></b-form-input>
        </b-form-group>
        <b-form-group
          label="长度/cm"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.productLength" type="number"></b-form-input>
        </b-form-group>
        <b-form-group
          label="宽度/cm"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.productWidth" type="number"></b-form-input>
        </b-form-group>
        <b-form-group
          label="高度/cm"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.productHeight" type="number"></b-form-input>
        </b-form-group>
        <b-form-group
          label="组合商品"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.isCombined"></b-form-input>
        </b-form-group>
        <b-form-group
          label="参与统计"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.beAggregated"></b-form-input>
        </b-form-group>
        <b-form-group
          label="进口商品"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.isImport"></b-form-input>
        </b-form-group>
        <b-form-group
          label="供应商名称"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.supplierName"></b-form-input>
        </b-form-group>
        <b-form-group
          label="采购名称"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.purchaseName"></b-form-input>
        </b-form-group>
        <b-form-group
          label="实时可用库存"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.jitInventory" type="number"></b-form-input>
        </b-form-group>
        <b-form-group
          label="最小订货单元"
          label-size="sm"
          label-align-sm="right"
          label-cols-sm="3"
        >
          <b-form-input v-model="updateProduct.moq" type="number"></b-form-input>
        </b-form-group>
        <br/>
        <div id="product-table-operate-btn" class="w-100 d-block">
          <b-button variant="dark" @click="onLoadOldProductData">加载旧数据</b-button>
          <b-button variant="dark" @click="onUpdateNewProductData">更新新数据</b-button>
          <b-button variant="dark" @click="onCancelUpdateNewProductData">取消</b-button>
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
    <b-modal ref="processingModal" hide-footer>
      <div class="d-flex align-items-center">
        <strong>处理中...</strong>
        <b-spinner class="ml-auto"></b-spinner>
      </div>
    </b-modal>
  </div>
</template>

<style>
#import-and-export-btn-area {
  margin-bottom: 10px;
}

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
import Navbar from './Navbar.vue'
import router from '../router'

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
      uploadUnitPriceCSVFile: null,
      adminUsr: '',
      adminPwd: '',
      specificationCode: '',
      updateProduct: {
        id: '',
        specificationCode: '',
        productCode: '',
        productName: '',
        specificationName: '',
        brand: '',
        classification1: '',
        classification2: '',
        productSeries: '',
        stopStatus: '',
        productWeight: '',
        productLength: '',
        productWidth: '',
        productHeight: '',
        isCombined: '',
        beAggregated: '',
        isImport: '',
        supplierName: '',
        purchaseName: '',
        jitInventory: '',
        moq: ''
      },
      message: '',
      showMessage: false
    }
  },
  components: {
    alert: Alert,
    navbar: Navbar
  },
  methods: {
    async listProducts () {
      await axios.get(this.serverBaseURL + `/api/v1/products/?page.offset=${this.pageOffset}&page.limit=20`)
        .then((res) => {
          const products = Object.freeze(res.data.products)
          this.products = products
          this.productsNum = res.data.products.length
          if (this.productsNum > 0) {
            this.pageCurr = this.pageOffset / 20 + 1
          } else {
            this.pageCurr = 0
          }
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
    },
    async getProductsTotal () {
      await axios.get(this.serverBaseURL + '/api/v1/products/total')
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
          if (error.response.status === 401) {
            router.push('/login')
          } else {
            // eslint-disable-next-line
            console.log(error)
            router.push('/500')
          }
        })
    },
    importProductCSVFileClose () {
      this.$refs.processingModal.hide()
      this.uploadProductCSVFile = null
    },
    importProductCSVFile (formData) {
      let config = {
        header: {
          'Content-Type': 'multipart/form-data'
        }
      }
      axios.post(this.serverBaseURL + '/api/v1/products/upload', formData, config)
        .then((res) => {
          this.message = '导入成功！预计导入' + res.data.items_total.toString() + '条，实际导入' + res.data.items_add.toString() + '条，去重' + res.data.items_exist.toString() + '条。'
          this.showMessage = true
          if (res.data.items_add > 0) {
            this.listProducts()
            this.getProductsTotal()
          }
          this.importProductCSVFileClose()
        })
        .catch((error) => {
          this.importProductCSVFileClose()
          if (error.response.status === 401) {
            router.push('/login')
          } else if (error.response.status === 400) {
            this.message = '导入失败！' + error.response.data.message
            this.showMessage = true
          } else if (error.response.status === 409) {
            this.message = '导入失败！数据表格重复导入！'
            this.showMessage = true
          } else {
            // eslint-disable-next-line
            console.log(error)
            router.push('/500')
          }
        })
    },
    importJITInventoryCSVFileClose () {
      this.$refs.processingModal.hide()
      this.uploadJITInventoryCSVFile = null
    },
    importJITInventoryCSVFile (formData) {
      let config = {
        header: {
          'Content-Type': 'multipart/form-data'
        }
      }
      axios.post(this.serverBaseURL + '/api/v1/jitinventory/upload', formData, config)
        .then((res) => {
          this.message = '导入成功!'
          this.showMessage = true
          this.listProducts()
          this.importJITInventoryCSVFileClose()
        })
        .catch((error) => {
          this.importJITInventoryCSVFileClose()
          if (error.response.status === 401) {
            router.push('/login')
          } else if (error.response.status === 400) {
            this.message = '导入失败！' + error.response.data.message
            this.showMessage = true
          } else if (error.response.status === 406) {
            this.message = '导入失败，有新增SKU，请人工复核！'
            this.showMessage = true
            this.addedSkus = error.data.added_skus
            this.shouldOpenSidebar = true
          } else if (error.response.status === 409) {
            this.message = '导入失败！数据表格重复导入！'
            this.showMessage = true
          } else {
            // eslint-disable-next-line
            console.log(error)
            router.push('/500')
          }
        })
    },
    importUnitPriceCSVFileClose () {
      this.$refs.processingModal.hide()
      this.uploadUnitPriceCSVFile = null
    },
    importUnitPriceCSVFile (formData) {
      let config = {
        header: {
          'Content-Type': 'multipart/form-data'
        }
      }
      axios.post(this.serverBaseURL + '/api/v1/unitprice/upload', formData, config)
        .then((res) => {
          this.message = '导入成功!'
          this.showMessage = true
          this.listProducts()
          this.importUnitPriceCSVFileClose()
        })
        .catch((error) => {
          this.importUnitPriceCSVFileClose()
          if (error.response.status === 401) {
            router.push('/login')
          } else if (error.response.status === 400) {
            this.message = '导入失败！' + error.response.data.message
            this.showMessage = true
          } else if (error.response.status === 406) {
            this.message = '导入失败，有新增SKU，请人工复核！'
            this.showMessage = true
            this.addedSkus = error.data.added_skus
            this.shouldOpenSidebar = true
          } else if (error.response.status === 409) {
            this.message = '导入失败！数据表格重复导入！'
            this.showMessage = true
          } else {
            // eslint-disable-next-line
            console.log(error)
            router.push('/500')
          }
        })
    },
    cleanAllProductsClose () {
      this.$refs.processingModal.hide()
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
    async cleanAllProducts (payload) {
      await axios.post(this.serverBaseURL + '/api/v1/products/all/clean', payload)
        .then((res) => {
          this.message = '删除成功！'
          this.showMessage = true
          this.cleanAllProductsClose()
        })
        .catch((error) => {
          this.cleanAllProductsClose()
          if (error.response.status === 401) {
            router.push('/login')
          } else if (error.response.status === 403) {
            this.message = '删除失败，管理员账号或密码错误！'
            this.showMessage = true
          } else {
            // eslint-disable-next-line
            console.log(error)
            router.push('/500')
          }
        })
    },
    cleanOneProductClose () {
      this.$refs.processingModal.hide()
      this.adminUsr = ''
      this.adminPwd = ''
      this.specificationCode = ''
    },
    async cleanOneProduct (payload) {
      await axios.post(this.serverBaseURL + '/api/v1/products/one/clean', payload)
        .then((res) => {
          this.message = '删除成功！'
          this.showMessage = true
          this.cleanOneProductClose()
        })
        .catch((error) => {
          this.cleanOneProductClose()
          if (error.response.status === 401) {
            router.push('/login')
          } else if (error.response.status === 403) {
            this.message = '删除失败，管理员账号或密码错误！'
            this.showMessage = true
          } else {
            // eslint-disable-next-line
            console.log(error)
            router.push('/500')
          }
        })
    },
    loadOldProductDataClose () {
      this.$refs.processingModal.hide()
    },
    async loadOldProductData (specificationCode) {
      await axios.get(this.serverBaseURL + '/api/v1/products/one/pick?specification_code=' + specificationCode)
        .then((res) => {
          this.updateProduct.id = res.data.product.id
          this.updateProduct.productCode = res.data.product.product_code
          this.updateProduct.productName = res.data.product.product_name
          this.updateProduct.specificationName = res.data.product.specification_name
          this.updateProduct.brand = res.data.product.brand
          this.updateProduct.classification1 = res.data.product.classification_1
          this.updateProduct.classification2 = res.data.product.classification_2
          this.updateProduct.productSeries = res.data.product.product_series
          this.updateProduct.stopStatus = res.data.product.stop_status
          this.updateProduct.productWeight = res.data.product.product_weight
          this.updateProduct.productLength = res.data.product.product_length
          this.updateProduct.productWidth = res.data.product.product_width
          this.updateProduct.productHeight = res.data.product.product_height
          this.updateProduct.isCombined = res.data.product.is_combined
          this.updateProduct.beAggregated = res.data.product.be_aggregated
          this.updateProduct.isImport = res.data.product.is_import
          this.updateProduct.supplierName = res.data.product.supplier_name
          this.updateProduct.purchaseName = res.data.product.purchase_name
          this.updateProduct.jitInventory = res.data.product.jit_inventory
          this.updateProduct.moq = res.data.product.moq
          this.message = '加载成功！'
          this.showMessage = true
          this.loadOldProductDataClose()
        })
        .catch((error) => {
          this.loadOldProductDataClose()
          if (error.response.status === 401) {
            router.push('/login')
          } else if (error.response.status === 404) {
            this.message = '加载失败！'
            this.showMessage = true
          } else {
            // eslint-disable-next-line
            console.log(error)
            router.push('/500')
          }
        })
    },
    updateNewProductDataClose () {
      this.$refs.processingModal.hide()
      this.updateProduct.id = ''
      this.updateProduct.specificationCode = ''
      this.updateProduct.productCode = ''
      this.updateProduct.productName = ''
      this.updateProduct.specificationName = ''
      this.updateProduct.brand = ''
      this.updateProduct.classification1 = ''
      this.updateProduct.classification2 = ''
      this.updateProduct.productSeries = ''
      this.updateProduct.stopStatus = ''
      this.updateProduct.productWeight = ''
      this.updateProduct.productLength = ''
      this.updateProduct.productWidth = ''
      this.updateProduct.productHeight = ''
      this.updateProduct.isCombined = ''
      this.updateProduct.beAggregated = ''
      this.updateProduct.isImport = ''
      this.updateProduct.supplierName = ''
      this.updateProduct.purchaseName = ''
      this.updateProduct.jitInventory = ''
      this.updateProduct.moq = ''
    },
    async updateNewProductData (payload) {
      await axios.post(this.serverBaseURL + '/api/v1/products/one/update', payload)
        .then((res) => {
          this.message = '更新成功！'
          this.showMessage = true
          this.updateNewProductDataClose()
        })
        .catch((error) => {
          this.updateNewProductDataClose()
          if (error.response.status === 401) {
            router.push('/login')
          } else {
            // eslint-disable-next-line
            console.log(error)
            router.push('/500')
          }
        })
    },
    preDownloadAddedSKUsClose () {
      this.$refs.processingModal.hide()
      this.shouldOpenSidebar = false
      this.addedSkus = []
    },
    async preDownloadAddedSKUs (payload) {
      await axios.post(this.serverBaseURL + '/api/v1/products/addedskus/prepare', payload)
        .then((res) => {
          this.downloadAddedSKUs(res.data.server_send_queue_file, res.data.output_file)
          this.preDownloadAddedSKUsClose()
        })
        .catch((error) => {
          this.preDownloadAddedSKUsClose()
          if (error.response.status === 401) {
            router.push('/login')
          } else {
            // eslint-disable-next-line
            console.log(error)
            router.push('/500')
          }
        })
    },
    async downloadAddedSKUs (queryFile, saveFile) {
      await axios.get(this.serverBaseURL + '/api/v1/common/download/' + queryFile)
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
          if (error.response.status === 401) {
            router.push('/login')
          } else {
            // eslint-disable-next-line
            console.log(error)
            router.push('/500')
          }
        })
    },
    onImportProducts (evt) {
      evt.preventDefault()
      if (this.uploadProductCSVFile === null) {
        this.message = '输入文件不能为空！'
        this.showMessage = true
      } else {
        this.$refs.importProductCSVFileModal.hide()
        this.$refs.processingModal.show()
        let formData = new FormData()
        formData.append('file', this.uploadProductCSVFile, this.uploadProductCSVFile.name)
        this.importProductCSVFile(formData)
      }
    },
    onCancelImportProducts (evt) {
      evt.preventDefault()
      this.$refs.importProductCSVFileModal.hide()
      this.uploadProductCSVFile = null
    },
    onImportJITInventory (evt) {
      evt.preventDefault()
      if (this.uploadJITInventoryCSVFile === null) {
        this.message = '输入文件不能为空！'
        this.showMessage = true
      } else {
        this.$refs.importJITInventoryCSVFileModal.hide()
        this.$refs.processingModal.show()
        let formData = new FormData()
        formData.append('file', this.uploadJITInventoryCSVFile, this.uploadJITInventoryCSVFile.name)
        this.importJITInventoryCSVFile(formData)
      }
    },
    onCancelImportJITInventory (evt) {
      evt.preventDefault()
      this.$refs.importJITInventoryCSVFileModal.hide()
      this.uploadJITInventoryCSVFile = null
    },
    onImportUnitPrice (evt) {
      evt.preventDefault()
      if (this.uploadUnitPriceCSVFile === null) {
        this.message = '输入文件不能为空！'
        this.showMessage = true
      } else {
        this.$refs.importUnitPriceCSVFileModal.hide()
        this.$refs.processingModal.show()
        let formData = new FormData()
        formData.append('file', this.uploadUnitPriceCSVFile, this.uploadUnitPriceCSVFile.name)
        this.importUnitPriceCSVFile(formData)
      }
    },
    onCancelImportUnitPrice (evt) {
      evt.preventDefault()
      this.$refs.importUnitPriceCSVFileModal.hide()
      this.uploadUnitPriceCSVFile = null
    },
    onCleanAllProducts (evt) {
      evt.preventDefault()
      this.$refs.CleanAllProductsModal.hide()
      this.$refs.processingModal.show()
      const payload = {
        admin_usr: this.adminUsr,
        admin_pwd: this.adminPwd
      }
      this.cleanAllProducts(payload)
    },
    onCancelCleanAllProducts (evt) {
      evt.preventDefault()
      this.$refs.CleanAllProductsModal.hide()
      this.adminUsr = ''
      this.adminPwd = ''
    },
    onLoadOldProductData (evt) {
      evt.preventDefault()
      this.$refs.processingModal.show()
      this.loadOldProductData(this.updateProduct.specificationCode)
    },
    onUpdateNewProductData (evt) {
      evt.preventDefault()
      this.$refs.updateOneProductModal.hide()
      this.$refs.processingModal.show()
      const payload = {
        id: this.updateProduct.id,
        specification_code: this.updateProduct.specificationCode,
        product_code: this.updateProduct.productCode,
        product_name: this.updateProduct.productName,
        specification_name: this.updateProduct.specificationName,
        brand: this.updateProduct.brand,
        classification_1: this.updateProduct.classification1,
        classification_2: this.updateProduct.classification2,
        product_series: this.updateProduct.productSeries,
        stop_status: this.updateProduct.stopStatus,
        product_weight: this.updateProduct.productWeight,
        product_length: this.updateProduct.productLength,
        product_width: this.updateProduct.productWidth,
        product_height: this.updateProduct.productHeight,
        is_combined: this.updateProduct.isCombined,
        be_aggregated: this.updateProduct.beAggregated,
        is_import: this.updateProduct.isImport,
        supplier_name: this.updateProduct.supplierName,
        purchase_name: this.updateProduct.purchaseName,
        jit_inventory: this.updateProduct.jitInventory,
        moq: this.updateProduct.moq
      }
      this.updateNewProductData(payload)
    },
    onCancelUpdateNewProductData (evt) {
      evt.preventDefault()
      this.$refs.updateOneProductModal.hide()
      this.updateProduct.specificationCode = ''
      this.updateProduct.productCode = ''
      this.updateProduct.productName = ''
      this.updateProduct.specificationName = ''
      this.updateProduct.brand = ''
      this.updateProduct.classification1 = ''
      this.updateProduct.classification2 = ''
      this.updateProduct.productSeries = ''
      this.updateProduct.stopStatus = ''
      this.updateProduct.productWeight = ''
      this.updateProduct.productLength = ''
      this.updateProduct.productWidth = ''
      this.updateProduct.productHeight = ''
      this.updateProduct.isCombined = ''
      this.updateProduct.beAggregated = ''
      this.updateProduct.isImport = ''
      this.updateProduct.supplierName = ''
      this.updateProduct.purchaseName = ''
      this.updateProduct.jitInventory = ''
      this.updateProduct.moq = ''
    },
    onCleanOneProduct (evt) {
      evt.preventDefault()
      this.$refs.CleanOneProductModal.hide()
      this.$refs.processingModal.show()
      const payload = {
        admin_usr: this.adminUsr,
        admin_pwd: this.adminPwd,
        specification_code: this.specificationCode
      }
      this.cleanOneProduct(payload)
    },
    onCancelCleanOneProduct (evt) {
      evt.preventDefault()
      this.$refs.CleanOneProductModal.hide()
      this.adminUsr = ''
      this.adminPwd = ''
      this.specificationCode = ''
    },
    onDownloadAddedSKUs (evt) {
      evt.preventDefault()
      this.$refs.processingModal.show()
      const payload = {
        added_skus: this.addedSkus
      }
      this.preDownloadAddedSKUs(payload)
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

    if (this.$cookies.isKey('logged')) {
      if (this.$cookies.get('logged') === 'in') {
        this.listProducts()
        this.getProductsTotal()
      } else {
        router.push('/login')
      }
    } else {
      router.push('/login')
    }
  }
}
</script>
