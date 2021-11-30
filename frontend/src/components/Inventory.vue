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
            v-model="importCSVFileForm.file"
            :state="Boolean(importCSVFileForm.file)"
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
      <b-form @submit="onExportCase3" @reset="onCancelCase3">
        <b-button-group id="inventory-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导出</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </b-button-group>
      </b-form>
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
</style>

<script>
import axios from 'axios'
import Alert from './Alert.vue'

export default {
  data () {
    return {
      inventories: [],
      pageOffset: 0,
      importCSVFileForm: {
        file: null
      },
      // 导出销售报表（按分类汇总）
      exportReportFileCase1Form: {},
      // 导出销售报表（按系列汇总）
      exportReportFileCase2Form: {},
      // 导出销售报表（按单个SKU汇总）
      exportReportFileCase3Form: {},
      // 导出滞销品报表
      exportReportFileCase4Form: {},
      // 导出进口产品采购单
      exportReportFileCase5Form: {},
      // 导出体积、重量计算汇总单
      exportReportFileCase6Form: {},
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
    importCSVFile (payload) {
      axios.post('http://localhost:5000/api/v1/inventories/import', payload)
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
    initImportForm () {
      this.importCSVFileForm.file = null
    },
    onImport (evt) {
      evt.preventDefault()
      this.$refs.importCSVFileModal.hide()
      const payload = {
        file: this.importCSVFileForm.file.name
      }
      this.importCSVFile(payload)
      this.initImportForm()
    },
    onCancel (evt) {
      evt.preventDefault()
      this.$refs.importCSVFileModal.hide()
      this.initImportForm()
    },
    exportReportFileCase1 (payload) {
      axios.post('http://localhost:5000/api/v1/export/case1', payload)
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
    initExportCase1Form () {
    },
    onExportCase1 (evt) {
      // 确定导出销售报表（按分类汇总）
      evt.preventDefault()
      this.$refs.exportFileCase1Modal.hide()
      console.log('确定导出销售报表（按分类汇总）')
      const payload = {}
      this.exportReportFileCase1(payload)
      this.initExportCase1Form()
    },
    onCancelCase1 (evt) {
      // 取消导出销售报表（按分类汇总）
      evt.preventDefault()
      this.$refs.exportFileCase1Modal.hide()
      console.log('取消导出销售报表（按分类汇总）')
      this.initExportCase1Form()
    },
    exportReportFileCase2 (payload) {
      axios.post('http://localhost:5000/api/v1/export/case2', payload)
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
    initExportCase2Form () {
    },
    onExportCase2 (evt) {
      // 确定导出销售报表（按系列汇总）
      evt.preventDefault()
      this.$refs.exportFileCase2Modal.hide()
      console.log('确定导出销售报表（按系列汇总）')
      const payload = {}
      this.exportReportFileCase2(payload)
      this.initExportCase2Form()
    },
    onCancelCase2 (evt) {
      // 取消导出销售报表（按系列汇总）
      evt.preventDefault()
      this.$refs.exportFileCase2Modal.hide()
      console.log('取消导出销售报表（按系列汇总）')
      this.initExportCase2Form()
    },
    exportReportFileCase3 (payload) {
      axios.post('http://localhost:5000/api/v1/export/case3', payload)
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
    initExportCase3Form () {
    },
    onExportCase3 (evt) {
      // 确定导出销售报表（按单个SKU汇总）
      evt.preventDefault()
      this.$refs.exportFileCase3Modal.hide()
      console.log('确定导出销售报表（按单个SKU汇总）')
      const payload = {}
      this.exportReportFileCase3(payload)
      this.initExportCase3Form()
    },
    onCancelCase3 (evt) {
      // 取消导出销售报表（按单个SKU汇总）
      evt.preventDefault()
      this.$refs.exportFileCase3Modal.hide()
      console.log('取消导出销售报表（按单个SKU汇总）')
      this.initExportCase3Form()
    },
    exportReportFileCase4 (payload) {
      axios.post('http://localhost:5000/api/v1/export/case4', payload)
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
    initExportCase4Form () {
    },
    onExportCase4 (evt) {
      // 确定导出滞销品报表
      evt.preventDefault()
      this.$refs.exportFileCase4Modal.hide()
      console.log('确定导出滞销品报表')
      const payload = {}
      this.exportReportFileCase4(payload)
      this.initExportCase4Form()
    },
    onCancelCase4 (evt) {
      // 取消导出滞销品报表
      evt.preventDefault()
      this.$refs.exportFileCase4Modal.hide()
      console.log('取消导出滞销品报表')
      this.initExportCase4Form()
    },
    exportReportFileCase5 (payload) {
      axios.post('http://localhost:5000/api/v1/export/case5', payload)
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
    initExportCase5Form () {
    },
    onExportCase5 (evt) {
      // 确定导出进口产品采购单
      evt.preventDefault()
      this.$refs.exportFileCase5Modal.hide()
      console.log('确定导出进口产品采购单')
      const payload = {}
      this.exportReportFileCase5(payload)
      this.initExportCase5Form()
    },
    onCancelCase5 (evt) {
      // 取消导出进口产品采购单
      evt.preventDefault()
      this.$refs.exportFileCase5Modal.hide()
      console.log('取消导出进口产品采购单')
      this.initExportCase5Form()
    },
    exportReportFileCase6 (payload) {
      axios.post('http://localhost:5000/api/v1/export/case6', payload)
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
    initExportCase6Form () {
    },
    onExportCase6 (evt) {
      // 确定导出体积、重量计算汇总单
      evt.preventDefault()
      this.$refs.exportFileCase6Modal.hide()
      console.log('确定导出体积、重量计算汇总单')
      const payload = {}
      this.exportReportFileCase6(payload)
      this.initExportCase6Form()
    },
    onCancelCase6 (evt) {
      // 取消导出体积、重量计算汇总单
      evt.preventDefault()
      this.$refs.exportFileCase6Modal.hide()
      console.log('取消导出体积、重量计算汇总单')
      this.initExportCase6Form()
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
  }
}
</script>
