<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-12">
        <b-navbar type="dark" variant="dark">
          <b-navbar-nav>
            <b-nav-item :active="false" href="/product">商品明细库</b-nav-item>
            <b-nav-item :active="false" href="/">库存明细库</b-nav-item>
            <b-nav-item :active="true" href="/slist">搜索项列表</b-nav-item>
            <b-nav-item :active="false" href="/oplog">操作日志</b-nav-item>
          </b-navbar-nav>
        </b-navbar>
      </div>
    </div>
    <br/>
    <div class="row" style="margin-bottom: 0; padding-bottom: 0;">
      <div class="col-sm-4">
      </div>
      <div class="col-sm-4" style="text-align: right;">
        <h5>提示：<b-badge>通过关联查询，导出关联标签</b-badge></h5>
      </div>
      <div class="col-sm-4">
      </div>
    </div>
    <div class="row" style="margin-top: 0; padding-top: 0;">
      <div class="col-sm-4">
      </div>
      <div class="col-sm-1" style="margin-right: 0; padding-right: 0;">
        <b-card bg-variant="dark" style="height: 600px;">
          <b-form-group class="selection-area">
            <b-avatar variant="secondary" size="6em">品牌</b-avatar>
          </b-form-group>
          <b-form-group class="selection-area">
            <b-avatar variant="secondary" size="6em">分类1</b-avatar>
          </b-form-group>
          <b-form-group class="selection-area">
            <b-avatar variant="secondary" size="6em">分类2</b-avatar>
          </b-form-group>
          <b-form-group class="selection-area">
            <b-avatar variant="secondary" size="6em">产品系列</b-avatar>
          </b-form-group>
          <b-form-group class="selection-area">
            <b-avatar variant="secondary" size="6em">供应商名称</b-avatar>
          </b-form-group>
        </b-card>
      </div>
      <div class="col-sm-3" style="margin-left: 0; padding-left: 0;">
        <b-card bg-variant="light" style="height: 600px;">
          <b-form-group
            class="selection-area"
          >
            <b-form-select v-model="brandSelection" :options="brandSelections" :select-size="1"></b-form-select>
            <b-button class="selection-area-btn" variant="dark" @click="onFetchAssociations1">关联查询</b-button>
          </b-form-group>
          <b-form-group
            class="selection-area"
          >
            <b-form-select v-model="classification1Selection" :options="classification1Selections" :select-size="1"></b-form-select>
            <b-button class="selection-area-btn" variant="dark" @click="onFetchAssociations2" :disabled="btnEnabled1 === false">关联查询</b-button>
          </b-form-group>
          <b-form-group
            class="selection-area"
          >
            <b-form-select v-model="classification2Selection" :options="classification2Selections" :select-size="1"></b-form-select>
            <b-button class="selection-area-btn" variant="dark" @click="onFetchAssociations3" :disabled="btnEnabled2 === false">关联查询</b-button>
          </b-form-group>
          <b-form-group
            class="selection-area"
          >
            <b-form-select v-model="productSeriesSelection" :options="productSeriesSelections" :select-size="1"></b-form-select>
            <b-button class="selection-area-btn" variant="dark" @click="onFetchAssociations4" :disabled="btnEnabled3 === false">关联查询</b-button>
          </b-form-group>
          <b-form-group
            class="selection-area"
          >
            <b-form-select v-model="supplierNameSelection" :options="supplierNameSelections" :select-size="1"></b-form-select>
          </b-form-group>
        </b-card>
      </div>
      <div class="col-sm-4">
      </div>
    </div>
  </div>
</template>

<style>
.selection-area {
  height: 100px;
  text-align: right;
}

.selection-area-btn {
  margin-top: 10px;
}
</style>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      serverBaseURL: process.env.SERVER_BASE_URL,
      brandSelections: [],
      brandSelection: '',
      classification1Selections: [],
      classification1Selection: '',
      classification2Selections: [],
      classification2Selection: '',
      productSeriesSelections: [],
      productSeriesSelection: '',
      supplierNameSelections: [],
      supplierNameSelection: '',
      btnEnabled1: false,
      btnEnabled2: false,
      btnEnabled3: false
    }
  },
  methods: {
    listAllBrandSelections () {
      axios.get(this.serverBaseURL + '/api/v1/brands')
        .then((res) => {
          this.brandSelections = res.data.brand_selections
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    onFetchAssociations1 () {
      this.btnEnabled1 = false
      this.btnEnabled2 = false
      this.btnEnabled3 = false
      this.classification1Selection = ''
      this.classification2Selection = ''
      this.productSeriesSelection = ''
      this.supplierNameSelection = ''
      const payload = {
        brand: this.brandSelection
      }
      axios.post(this.serverBaseURL + '/api/v1/associations', payload)
        .then((res) => {
          this.classification1Selections = res.data.classification_1_selections
          if (this.classification1Selections.length > 0) {
            this.btnEnabled1 = true
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    onFetchAssociations2 () {
      this.classification2Selection = ''
      this.productSeriesSelection = ''
      this.supplierNameSelection = ''
      const payload = {
        brand: this.brandSelection,
        classification_1: this.classification1Selection
      }
      axios.post(this.serverBaseURL + '/api/v1/associations', payload)
        .then((res) => {
          this.classification2Selections = res.data.classification_2_selections
          if (this.classification2Selections.length > 0) {
            this.btnEnabled2 = true
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    onFetchAssociations3 () {
      this.productSeriesSelection = ''
      this.supplierNameSelection = ''
      const payload = {
        brand: this.brandSelection,
        classification_1: this.classification1Selection,
        classification_2: this.classification2Selection
      }
      axios.post(this.serverBaseURL + '/api/v1/associations', payload)
        .then((res) => {
          this.productSeriesSelections = res.data.product_series_selections
          if (this.productSeriesSelections.length > 0) {
            this.btnEnabled3 = true
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    onFetchAssociations4 () {
      this.supplierNameSelection = ''
      const payload = {
        brand: this.brandSelection,
        classification_1: this.classification1Selection,
        classification_2: this.classification2Selection,
        product_series: this.productSeriesSelection
      }
      axios.post(this.serverBaseURL + '/api/v1/associations', payload)
        .then((res) => {
          this.supplierNameSelections = res.data.supplier_name_selections
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    }
  },
  created () {
    console.log(process.env.NODE_ENV)
    console.log(process.env.SERVER_BASE_URL)
    this.listAllBrandSelections()
  }
}
</script>
