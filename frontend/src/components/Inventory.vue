<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-12">
        <h1>库存明细库</h1>
        <hr>
        <alert :message=message v-if="showMessage"></alert>
        <div id="import-and-export-btn-area">
          <button type="button" class="btn btn-success btn-sm" v-b-modal.csv-file-modal>导入库存数据</button>
          <b-dropdown text="导出定制报表" variant="success" size="sm">
            <b-dropdown-header id="dropdown-header-1"><strong>销售报表</strong></b-dropdown-header>
            <b-dropdown-item-button aria-describedby="dropdown-header-1" variant="secondary" v-b-modal.export-file-case1-modal>
              按分类汇总导出
            </b-dropdown-item-button>
            <b-dropdown-item-button aria-describedby="dropdown-header-1" variant="secondary" v-b-modal.export-file-case2-modal>
              按系列汇总导出
            </b-dropdown-item-button>
            <b-dropdown-item-button aria-describedby="dropdown-header-1" variant="secondary" v-b-modal.export-file-case3-modal>
              按单个SKU汇总导出
            </b-dropdown-item-button>
            <b-dropdown-divider></b-dropdown-divider>
            <b-dropdown-header id="dropdown-header-2"><strong>滞销品报表</strong></b-dropdown-header>
            <b-dropdown-item-button aria-describedby="dropdown-header-2" variant="secondary" v-b-modal.export-file-case4-modal>
              导出
            </b-dropdown-item-button>
            <b-dropdown-divider></b-dropdown-divider>
            <b-dropdown-header id="dropdown-header-3"><strong>进口产品采购单</strong></b-dropdown-header>
            <b-dropdown-item-button aria-describedby="dropdown-header-3" variant="secondary" v-b-modal.export-file-case5-modal>
              导出
            </b-dropdown-item-button>
            <b-dropdown-divider></b-dropdown-divider>
            <b-dropdown-header id="dropdown-header-4"><strong>体积、重量计算汇总单</strong></b-dropdown-header>
            <b-dropdown-item-button aria-describedby="dropdown-header-4" variant="secondary" v-b-modal.export-file-case6-modal>
              导出
            </b-dropdown-item-button>
          </b-dropdown>
        </div>
        <br/>
        <b-table-simple striped hover small id="inventory-table">
          <b-thead>
            <b-tr>
              <b-th scope="col">导入日期</b-th>
              <b-th scope="col">商品编号</b-th>
              <b-th scope="col">商品名称</b-th>
              <b-th scope="col">规格编号</b-th>
              <b-th scope="col">规格名称</b-th>
              <b-th scope="col">起始库存数量</b-th>
              <b-th scope="col">起始库存总额</b-th>
              <b-th scope="col">采购数量</b-th>
              <b-th scope="col">采购总额</b-th>
              <b-th scope="col">采购退货数量</b-th>
              <b-th scope="col">采购退货总额</b-th>
              <b-th scope="col">销售数量</b-th>
              <b-th scope="col">销售总额</b-th>
              <b-th scope="col">销售退货数量</b-th>
              <b-th scope="col">销售退货总额</b-th>
              <b-th scope="col">其他变更数量</b-th>
              <b-th scope="col">其他变更总额</b-th>
              <b-th scope="col">截止库存数量</b-th>
              <b-th scope="col">截止库存总额</b-th>
            </b-tr>
          </b-thead>
          <b-tbody>
            <b-tr v-for="(inventory, index) in inventories" :key="index">
              <b-td>{{ inventory[18] }}</b-td>
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
        </b-table-simple>
        <div id="pagination-btn-area">
          <button class="btn btn-success btn-sm" :disabled="pageOffset==0" v-on:click="onPrevPage">前一页</button>
          <button class="btn btn-success btn-sm" v-on:click="onNextPage">后一页</button>
        </div>
      </div>
    </div>
    <b-modal ref="importCSVFileModal" id="csv-file-modal" title="导入库存数据" hide-footer>
      <b-form @submit="onImport" @reset="onCancel">
        <b-form-group>
          <b-form-file
            accept=".csv"
            v-model="uploadCSVFile"
            :state="Boolean(uploadCSVFile)"
            placeholder="请选择UTF-8编码的CSV文件">
          </b-form-file>
        </b-form-group>
        <br/>
        <b-button-group id="inventory-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导入</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
    <b-modal ref="exportFileCase1Modal" id="export-file-case1-modal" title="导出销售报表（按分类汇总）" hide-footer>
      <b-form @submit="onExportCase1" @reset="onCancelCase1">
        <b-button-group id="inventory-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导出</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
    <b-modal ref="exportFileCase2Modal" id="export-file-case2-modal" title="导出销售报表（按系列汇总）" hide-footer>
      <b-form @submit="onExportCase2" @reset="onCancelCase2">
        <b-button-group id="inventory-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导出</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
    <b-modal ref="exportFileCase3Modal" id="export-file-case3-modal" title="导出销售报表（按单个SKU汇总）" hide-footer>
      <b-form>
        <b-card bg-variant="light">
          <b-form-group
            label="起始日期"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-input-group>
              <b-form-input
                v-model="stDateSelection"
                type="text"
                placeholder="YYYY-MM-DD"
                autocomplete="off"
              ></b-form-input>
              <b-input-group-append>
                <b-form-datepicker
                  v-model="stDateSelection"
                  button-only
                  right
                  locale="zh-CH"
                ></b-form-datepicker>
              </b-input-group-append>
            </b-input-group>
          </b-form-group>
          <b-form-group
            label="截止日期"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-input-group>
              <b-form-input
                v-model="edDateSelection"
                type="text"
                placeholder="YYYY-MM-DD"
                autocomplete="off"
              ></b-form-input>
              <b-input-group-append>
                <b-form-datepicker
                  v-model="edDateSelection"
                  button-only
                  right
                  locale="zh-CH"
                ></b-form-datepicker>
              </b-input-group-append>
            </b-input-group>
          </b-form-group>
          <b-form-group
            label="商品编码"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-input v-model="productCodeSelection"></b-form-input>
          </b-form-group>
          <b-form-group
            label="商品名称"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-input v-model="productNameSelection"></b-form-input>
          </b-form-group>
          <b-form-group
            label="规格编码"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-input v-model="specificationCodeSelection"></b-form-input>
          </b-form-group>
          <b-form-group
            label="品牌"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <v-suggest
              :data="brandSelections"
              show-field="brand"
              v-model="brandSelection"
            ></v-suggest>
          </b-form-group>
          <b-form-group
            label="分类1"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <v-suggest
              :data="classification1Selections"
              show-field="classification-1"
              v-model="classification1Selection"
            ></v-suggest>
          </b-form-group>
          <b-form-group
            label="分类2"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <v-suggest
              :data="classification2Selections"
              show-field="classification-2"
              v-model="classification2Selection"
            ></v-suggest>
          </b-form-group>
          <b-form-group
            label="产品系列"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <v-suggest
              :data="productSeriesSelections"
              show-field="product-series"
              v-model="productSeriesSelection"
            ></v-suggest>
          </b-form-group>
          <b-form-group
            label="STOP状态?"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-select v-model="stopStatusSelection" :options="stopStatusSelections"></b-form-select>
          </b-form-group>
          <b-form-group
            label="组合商品?"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-select v-model="isCombinedSelection" :options="isCombinedSelections"></b-form-select>
          </b-form-group>
          <b-form-group
            label="参与统计?"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-select v-model="beAggregatedSelection" :options="beAggregatedSelections"></b-form-select>
          </b-form-group>
          <b-form-group
            label="进口商品?"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-select v-model="isImportSelection" :options="isImportSelections"></b-form-select>
          </b-form-group>
          <b-form-group
            label="供应商名称"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <v-suggest
              :data="supplierNameSelections"
              show-field="supplier-name"
              v-model="supplierNameSelection"
            ></v-suggest>
          </b-form-group>
          <b-button-group id="inventory-table-operate-btn" class="w-100 d-block">
            <b-button variant="dark" @click="onPreviewCase3">预览</b-button>
            <b-button variant="dark" @click="onCancelCase3">取消</b-button>
          </b-button-group>
        </b-card>
      </b-form>
    </b-modal>
    <b-modal ref="previewCase3Modal" title="预览销售报表（按单个SKU汇总）" size="lg" hide-footer>
      <b-table-simple striped hover small id="preview-case3-table">
        <b-thead>
          <b-tr>
            <b-th scope="col">商品编号</b-th>
            <b-th scope="col">规格编号</b-th>
            <b-th scope="col">商品名称</b-th>
            <b-th scope="col">规格名称</b-th>
            <b-th scope="col">起始库存数量</b-th>
            <b-th scope="col">采购数量</b-th>
            <b-th scope="col">销售数量</b-th>
            <b-th scope="col">截止库存数量</b-th>
            <b-th scope="col">实时库存</b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr>
            <b-td>{{ previewCase3.productCode }}</b-td>
            <b-td>{{ previewCase3.specificationCode }}</b-td>
            <b-td>{{ previewCase3.productName }}</b-td>
            <b-td>{{ previewCase3.specificationName }}</b-td>
            <b-td>{{ previewCase3.stInventoryQty }}</b-td>
            <b-td>{{ previewCase3.purchaseQty }}</b-td>
            <b-td>{{ previewCase3.saleQty }}</b-td>
            <b-td>{{ previewCase3.edInventoryQty }}</b-td>
            <b-td>{{ previewCase3.jitInventory}}</b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
      <b-button-group id="inventory-table-operate-btn" class="w-100 d-block">
        <b-button variant="dark" @click="onExportCase3">导出</b-button>
        <b-button variant="dark" @click="onCancelPreviewCase3">取消</b-button>
      </b-button-group>
    </b-modal>
    <b-modal ref="exportFileCase4Modal" id="export-file-case4-modal" title="导出滞销品报表" hide-footer>
      <b-form @submit="onExportCase4" @reset="onCancelCase4">
        <b-button-group id="inventory-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导出</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
    <b-modal ref="exportFileCase5Modal" id="export-file-case5-modal" title="导出进口产品采购单" hide-footer>
      <b-form @submit="onExportCase5" @reset="onCancelCase5">
        <b-button-group id="inventory-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导出</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
    <b-modal ref="exportFileCase6Modal" id="export-file-case6-modal" title="导出体积、重量计算汇总单" hide-footer>
      <b-form @submit="onExportCase6" @reset="onCancelCase6">
        <b-button-group id="inventory-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导出</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </b-button-group>
      </b-form>
    </b-modal>
  </div>
</template>

<style>
#inventory-table {
  border: 2px solid black !important;
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

#pagination-btn-area {
  text-align: center;
}

#inventory-table-operate-btn {
  text-align: right;
}

#preview-case3-table {
  border: 2px solid black !important;
  font-size: small;
  table-layout: fixed !important;
}
</style>

<script>
import axios from 'axios'
import Alert from './Alert.vue'
import { Suggest } from 'v-suggest'

export default {
  data () {
    return {
      serverBaseURL: process.env.SERVER_BASE_URL,
      stDateSelection: '',
      edDateSelection: '',
      productCodeSelection: '',
      productNameSelection: '',
      specificationCodeSelection: '',
      brandSelections: [],
      brandSelection: '',
      classification1Selections: [],
      classification1Selection: '',
      classification2Selections: [],
      classification2Selection: '',
      productSeriesSelections: [],
      productSeriesSelection: '',
      stopStatusSelections: [
        { value: '在用', text: '在用' },
        { value: '停用', text: '停用' }
      ],
      stopStatusSelection: '在用',
      isCombinedSelections: [
        { value: '是', text: '是' },
        { value: '否', text: '否' }
      ],
      isCombinedSelection: '否',
      beAggregatedSelections: [
        { value: '参与', text: '参与' },
        { value: '不参与', text: '不参与' }
      ],
      beAggregatedSelection: '参与',
      isImportSelections: [
        { value: '进口品', text: '进口品' },
        { value: '非进口品', text: '非进口品' }
      ],
      isImportSelection: '非进口品',
      supplierNameSelections: [],
      supplierNameSelection: '',
      inventories: [],
      pageOffset: 0,
      uploadCSVFile: null,
      previewCase3: {
        productCode: '',
        specificationCode: '',
        productName: '',
        specificationName: '',
        stInventoryQty: 0,
        purchaseQty: 0,
        saleQty: 0,
        edInventoryQty: 0,
        jitInventory: 0
      },
      message: '',
      showMessage: false
    }
  },
  components: {
    alert: Alert,
    'v-suggest': Suggest
  },
  methods: {
    listAllSelections () {
      axios.get(this.serverBaseURL + '/api/v1/allselections')
        .then((res) => {
          this.brandSelections = res.data.brand_selections
          console.log(this.brandSelections.length)
          this.classification1Selections = res.data.classification_1_selections
          console.log(this.classification1Selections.length)
          this.classification2Selections = res.data.classification_2_selections
          console.log(this.classification2Selections.length)
          this.productSeriesSelections = res.data.product_series_selections
          console.log(this.productSeriesSelections.length)
          this.supplierNameSelections = res.data.supplier_name_selections
          console.log(this.supplierNameSelections.length)
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误!'
          this.showMessage = true
        })
    },
    listInventories () {
      axios.get(this.serverBaseURL + `/api/v1/inventories?page.offset=${this.pageOffset}&page.limit=20`)
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
    initExportForm () {
      this.stDateSelection = ''
      this.edDateSelection = ''
      this.productCodeSelection = ''
      this.productNameSelection = ''
      this.specificationCodeSelection = ''
      this.brandSelection = ''
      this.classification1Selection = ''
      this.classification2Selection = ''
      this.productSeriesSelection = ''
      this.stopStatusSelection = '在用'
      this.isCombinedSelection = '否'
      this.beAggregatedSelection = '参与'
      this.isImportSelection = '非进口品'
      this.supplierNameSelection = ''
      this.uploadCSVFile = null
      this.previewCase3.productCode = ''
      this.previewCase3.specificationCode = ''
      this.previewCase3.productName = ''
      this.previewCase3.specificationName = ''
      this.previewCase3.stInventoryQty = 0
      this.previewCase3.purchaseQty = 0
      this.previewCase3.saleQty = 0
      this.previewCase3.edInventoryQty = 0
      this.previewCase3.jitInventory = 0
    },
    importCSVFile (formData) {
      let config = {
        header: {
          'Content-Type': 'multipart/form-data'
        }
      }
      axios.post(this.serverBaseURL + '/api/v1/inventories/upload', formData, config)
        .then(() => {
          this.listInventories()
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
    onImport (evt) {
      evt.preventDefault()
      this.$refs.importCSVFileModal.hide()
      let formData = new FormData()
      formData.append('file', this.uploadCSVFile, this.uploadCSVFile.name)
      this.importCSVFile(formData)
    },
    onCancel (evt) {
      evt.preventDefault()
      this.$refs.importCSVFileModal.hide()
    },
    exportReportFileCase1 (payload) {
      axios.post(this.serverBaseURL + '/api/v1/export/case1', payload)
        .then((res) => {
          console.log(res.data)
          this.message = '导出成功!'
          this.showMessage = true
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '导出失败!'
          this.showMessage = true
        })
    },
    onExportCase1 (evt) {
      // 确定导出销售报表（按分类汇总）
      evt.preventDefault()
      this.$refs.exportFileCase1Modal.hide()
      console.log('确定导出销售报表（按分类汇总）')
      const payload = {}
      this.exportReportFileCase1(payload)
      this.initExportForm()
    },
    onCancelCase1 (evt) {
      // 取消导出销售报表（按分类汇总）
      evt.preventDefault()
      this.$refs.exportFileCase1Modal.hide()
      console.log('取消导出销售报表（按分类汇总）')
      this.initExportForm()
    },
    exportReportFileCase2 (payload) {
      axios.post(this.serverBaseURL + '/api/v1/export/case2', payload)
        .then((res) => {
          console.log(res.data)
          this.message = '导出成功!'
          this.showMessage = true
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '导出失败!'
          this.showMessage = true
        })
    },
    onExportCase2 (evt) {
      // 确定导出销售报表（按系列汇总）
      evt.preventDefault()
      this.$refs.exportFileCase2Modal.hide()
      console.log('确定导出销售报表（按系列汇总）')
      const payload = {}
      this.exportReportFileCase2(payload)
      this.initExportForm()
    },
    onCancelCase2 (evt) {
      // 取消导出销售报表（按系列汇总）
      evt.preventDefault()
      this.$refs.exportFileCase2Modal.hide()
      console.log('取消导出销售报表（按系列汇总）')
      this.initExportForm()
    },
    exportPreviewReportFileCase3 (payload) {
      axios.post(this.serverBaseURL + '/api/v1/export/case3/preview', payload)
        .then((res) => {
          if (res.data.status === 'success') {
            this.previewCase3.productCode = res.data.product_code
            this.previewCase3.specificationCode = res.data.specification_code
            this.previewCase3.productName = res.data.product_name
            this.previewCase3.specificationName = res.data.specification_name
            this.previewCase3.stInventoryQty = res.data.st_inventory_qty
            this.previewCase3.purchaseQty = res.data.purchase_qty
            this.previewCase3.saleQty = res.data.sale_qty
            this.previewCase3.edInventoryQty = res.data.ed_inventory_qty
            this.previewCase3.jitInventory = res.data.jit_inventory
            this.$refs.previewCase3Modal.show()
          } else {
            this.message = '预览失败! 不存在指定的库存条目.'
            this.showMessage = true
            this.initExportForm()
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '预览失败!'
          this.showMessage = true
        })
    },
    onPreviewCase3 (evt) {
      // 预览销售报表（按单个SKU汇总）
      evt.preventDefault()
      if ((this.stDateSelection === '') || (this.edDateSelection === '')) {
        this.message = '起始日期/截止日期不能为空!'
        this.showMessage = true
      } else {
        const payload = {
          st_date: this.stDateSelection,
          ed_date: this.edDateSelection,
          product_code: this.productCodeSelection,
          product_name: this.productNameSelection,
          specification_code: this.specificationCodeSelection,
          brand: this.brandSelection,
          classification_1: this.classification1Selection,
          classification_2: this.classification2Selection,
          product_series: this.productSeriesSelection,
          stop_status: this.stopStatusSelection,
          is_combined: this.isCombinedSelection,
          be_aggregated: this.beAggregatedSelection,
          is_import: this.isImportSelection,
          supplier_name: this.supplierNameSelection
        }
        this.exportPreviewReportFileCase3(payload)
      }
    },
    onCancelPreviewCase3 (evt) {
      evt.preventDefault()
      this.$refs.previewCase3Modal.hide()
      this.initExportForm()
    },
    onExportCase3 (evt) {
      // 确定导出销售报表（按单个SKU汇总）
      evt.preventDefault()
      this.$refs.exportFileCase3Modal.hide()
      this.initExportForm()
    },
    onCancelCase3 (evt) {
      // 取消导出销售报表（按单个SKU汇总）
      evt.preventDefault()
      this.$refs.exportFileCase3Modal.hide()
      console.log('取消导出销售报表（按单个SKU汇总）')
      this.initExportForm()
    },
    exportReportFileCase4 (payload) {
      axios.post(this.serverBaseURL + '/api/v1/export/case4', payload)
        .then((res) => {
          console.log(res.data)
          this.message = '导出成功!'
          this.showMessage = true
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '导出失败!'
          this.showMessage = true
        })
    },
    onExportCase4 (evt) {
      // 确定导出滞销品报表
      evt.preventDefault()
      this.$refs.exportFileCase4Modal.hide()
      console.log('确定导出滞销品报表')
      const payload = {}
      this.exportReportFileCase4(payload)
      this.initExportForm()
    },
    onCancelCase4 (evt) {
      // 取消导出滞销品报表
      evt.preventDefault()
      this.$refs.exportFileCase4Modal.hide()
      console.log('取消导出滞销品报表')
      this.initExportForm()
    },
    exportReportFileCase5 (payload) {
      axios.post(this.serverBaseURL + '/api/v1/export/case5', payload)
        .then((res) => {
          console.log(res.data)
          this.message = '导出成功!'
          this.showMessage = true
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '导出失败!'
          this.showMessage = true
        })
    },
    onExportCase5 (evt) {
      // 确定导出进口产品采购单
      evt.preventDefault()
      this.$refs.exportFileCase5Modal.hide()
      console.log('确定导出进口产品采购单')
      const payload = {}
      this.exportReportFileCase5(payload)
      this.initExportForm()
    },
    onCancelCase5 (evt) {
      // 取消导出进口产品采购单
      evt.preventDefault()
      this.$refs.exportFileCase5Modal.hide()
      console.log('取消导出进口产品采购单')
      this.initExportForm()
    },
    exportReportFileCase6 (payload) {
      axios.post(this.serverBaseURL + '/api/v1/export/case6', payload)
        .then((res) => {
          console.log(res.data)
          this.message = '导出成功!'
          this.showMessage = true
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '导出失败!'
          this.showMessage = true
        })
    },
    onExportCase6 (evt) {
      // 确定导出体积、重量计算汇总单
      evt.preventDefault()
      this.$refs.exportFileCase6Modal.hide()
      console.log('确定导出体积、重量计算汇总单')
      const payload = {}
      this.exportReportFileCase6(payload)
      this.initExportForm()
    },
    onCancelCase6 (evt) {
      // 取消导出体积、重量计算汇总单
      evt.preventDefault()
      this.$refs.exportFileCase6Modal.hide()
      console.log('取消导出体积、重量计算汇总单')
      this.initExportForm()
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
    console.log(process.env.NODE_ENV)
    console.log(process.env.SERVER_BASE_URL)
    this.listAllSelections()
    this.listInventories()
  }
}
</script>
