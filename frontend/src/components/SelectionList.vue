<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-12">
        <b-navbar type="dark" variant="dark">
          <b-navbar-nav>
            <b-nav-item :active="false" href="/product">商品明细库</b-nav-item>
            <b-nav-item :active="false" href="/">库存明细库</b-nav-item>
            <b-nav-item :active="true" href="/slist">辅助查询</b-nav-item>
            <b-nav-item :active="false" href="/oplog">操作日志</b-nav-item>
          </b-navbar-nav>
        </b-navbar>
      </div>
    </div>
    <br/>
    <div class="row">
      <div class="col-sm-12">
        <alert :message=message v-if="showMessage"></alert>
      </div>
    </div>
    <div class="row">
      <div class="col-sm-12">
        <h6>提示：<b-badge>点击“关联查询”按钮，导出下一级关联标签；点击“复制结果”按钮，结果自动复制到剪切板</b-badge></h6>
      </div>
    </div>
    <div class="row" style="margin-bottom: 0; padding-bottom: 0;">
      <div class="col-sm-4 selection-region-1">
        <div class="row">
          <div class="col-sm-3" style="margin-right: 0; padding-right: 0;">
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
          <div class="col-sm-9" style="margin-left: 0; padding-left: 0;">
            <b-card bg-variant="light" style="height: 600px;">
              <b-form-group
                class="selection-area"
              >
                <b-form-select v-model="region1.brandSelection" :options="region1.brandSelections" :select-size="1"></b-form-select>
                <div class="w-100 d-block">
                  <b-button class="selection-area-btn" variant="dark" @click="onRegion1FetchAssociations1">关联查询</b-button>
                  <b-button class="selection-area-btn" variant="dark" @click="copyText(region1.brandSelection)">复制结果</b-button>
                </div>
              </b-form-group>
              <b-form-group
                class="selection-area"
              >
                <b-form-select v-model="region1.classification1Selection" :options="region1.classification1Selections" :select-size="1"></b-form-select>
                <div class="w-100 d-block">
                  <b-button class="selection-area-btn" variant="dark" @click="onRegion1FetchAssociations2" :disabled="region1.btnEnabled1 === false">关联查询</b-button>
                  <b-button class="selection-area-btn" variant="dark" @click="copyText(region1.classification1Selection)">复制结果</b-button>
                </div>
              </b-form-group>
              <b-form-group
                class="selection-area"
              >
                <b-form-select v-model="region1.classification2Selection" :options="region1.classification2Selections" :select-size="1"></b-form-select>
                <div class="w-100 d-block">
                  <b-button class="selection-area-btn" variant="dark" @click="onRegion1FetchAssociations3" :disabled="region1.btnEnabled2 === false">关联查询</b-button>
                  <b-button class="selection-area-btn" variant="dark" @click="copyText(region1.classification2Selection)">复制结果</b-button>
                </div>
              </b-form-group>
              <b-form-group
                class="selection-area"
              >
                <b-form-select v-model="region1.productSeriesSelection" :options="region1.productSeriesSelections" :select-size="1"></b-form-select>
                <div class="w-100 d-block">
                  <b-button class="selection-area-btn" variant="dark" @click="onRegion1FetchAssociations4" :disabled="region1.btnEnabled3 === false">关联查询</b-button>
                  <b-button class="selection-area-btn" variant="dark" @click="copyText(region1.productSeriesSelection)">复制结果</b-button>
                </div>
              </b-form-group>
              <b-form-group
                class="selection-area"
              >
                <b-form-select v-model="region1.supplierNameSelection" :options="region1.supplierNameSelections" :select-size="1"></b-form-select>
                <div class="w-100 d-block">
                  <b-button class="selection-area-btn" variant="dark" @click="copyText(region1.supplierNameSelection)">复制结果</b-button>
                </div>
              </b-form-group>
            </b-card>
          </div>
        </div>
      </div>
      <div class="col-sm-4 selection-region-2">
        <div class="row">
          <div class="col-sm-3" style="margin-right: 0; padding-right: 0;">
            <b-card bg-variant="dark" style="height: 600px;">
              <b-form-group class="selection-area">
                <b-avatar variant="secondary" size="6em">分类1</b-avatar>
              </b-form-group>
              <b-form-group class="selection-area">
                <b-avatar variant="secondary" size="6em">分类2</b-avatar>
              </b-form-group>
            </b-card>
          </div>
          <div class="col-sm-9" style="margin-left: 0; padding-left: 0;">
            <b-card bg-variant="light" style="height: 600px;">
              <b-form-group
                class="selection-area"
              >
                <b-form-select v-model="region2.classification1Selection" :options="region2.classification1Selections" :select-size="1"></b-form-select>
                <div class="w-100 d-block">
                  <b-button class="selection-area-btn" variant="dark" @click="onRegion2FetchAssociations">关联查询</b-button>
                  <b-button class="selection-area-btn" variant="dark" @click="copyText(region2.classification1Selection)">复制结果</b-button>
                </div>
              </b-form-group>
              <b-form-group
                class="selection-area"
              >
                <b-form-select v-model="region2.classification2Selection" :options="region2.classification2Selections" :select-size="1"></b-form-select>
                <div class="w-100 d-block">
                  <b-button class="selection-area-btn" variant="dark" @click="copyText(region2.classification2Selection)">复制结果</b-button>
                </div>
              </b-form-group>
            </b-card>
          </div>
        </div>
      </div>
      <div class="col-sm-4 selection-region-3">
        <div class="row">
          <div class="col-sm-3" style="margin-right: 0; padding-right: 0;">
            <b-card bg-variant="dark" style="height: 600px;">
              <b-form-group class="selection-area">
                <b-avatar variant="secondary" size="6em">品牌</b-avatar>
              </b-form-group>
              <b-form-group class="selection-area">
                <b-avatar variant="secondary" size="6em">分类2</b-avatar>
              </b-form-group>
            </b-card>
          </div>
          <div class="col-sm-9" style="margin-left: 0; padding-left: 0;">
            <b-card bg-variant="light" style="height: 600px;">
              <b-form-group
                class="selection-area"
              >
                <b-form-select v-model="region3.brandSelection" :options="region3.brandSelections" :select-size="1"></b-form-select>
                <div class="w-100 d-block">
                  <b-button class="selection-area-btn" variant="dark" @click="onRegion3FetchAssociations">关联查询</b-button>
                  <b-button class="selection-area-btn" variant="dark" @click="copyText(region3.brandSelection)">复制结果</b-button>
                </div>
              </b-form-group>
              <b-form-group
                class="selection-area"
              >
                <b-form-select v-model="region3.classification2Selection" :options="region3.classification2Selections" :select-size="1"></b-form-select>
                <div class="w-100 d-block">
                  <b-button class="selection-area-btn" variant="dark" @click="copyText(region3.classification2Selection)">复制结果</b-button>
                </div>
              </b-form-group>
            </b-card>
          </div>
        </div>
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
import Alert from './Alert.vue'

export default {
  data () {
    return {
      serverBaseURL: process.env.SERVER_BASE_URL,
      region1: {
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
      },
      region2: {
        classification1Selections: [],
        classification1Selection: '',
        classification2Selections: [],
        classification2Selection: ''
      },
      region3: {
        brandSelections: [],
        brandSelection: '',
        classification2Selections: [],
        classification2Selection: ''
      },
      message: '',
      showMessage: false
    }
  },
  components: {
    alert: Alert
  },
  methods: {
    listAllBrandSelections () {
      axios.get(this.serverBaseURL + '/api/v1/brands')
        .then((res) => {
          this.region1.brandSelections = res.data.brand_selections
          this.region3.brandSelections = res.data.brand_selections
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    listAllClassification1Selections () {
      axios.get(this.serverBaseURL + '/api/v1/classification1')
        .then((res) => {
          this.region2.classification1Selections = res.data.classification_1_selections
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    onRegion1FetchAssociations1 (evt) {
      evt.preventDefault()
      this.region1.btnEnabled1 = false
      this.region1.btnEnabled2 = false
      this.region1.btnEnabled3 = false
      this.region1.classification1Selection = ''
      this.region1.classification2Selection = ''
      this.region1.productSeriesSelection = ''
      this.region1.supplierNameSelection = ''
      const payload = {
        brand: this.region1.brandSelection
      }
      axios.post(this.serverBaseURL + '/api/v1/associations/bc1c2', payload)
        .then((res) => {
          this.region1.classification1Selections = res.data.classification_1_selections
          if (this.region1.classification1Selections.length > 0) {
            this.region1.btnEnabled1 = true
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    onRegion1FetchAssociations2 (evt) {
      evt.preventDefault()
      this.region1.btnEnabled2 = false
      this.region1.btnEnabled3 = false
      this.region1.classification2Selection = ''
      this.region1.productSeriesSelection = ''
      this.region1.supplierNameSelection = ''
      const payload = {
        brand: this.region1.brandSelection,
        classification_1: this.region1.classification1Selection
      }
      axios.post(this.serverBaseURL + '/api/v1/associations/bc1c2', payload)
        .then((res) => {
          this.region1.classification2Selections = res.data.classification_2_selections
          if (this.region1.classification2Selections.length > 0) {
            this.region1.btnEnabled2 = true
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    onRegion1FetchAssociations3 (evt) {
      evt.preventDefault()
      this.region1.btnEnabled3 = false
      this.region1.productSeriesSelection = ''
      this.region1.supplierNameSelection = ''
      const payload = {
        brand: this.region1.brandSelection,
        classification_1: this.region1.classification1Selection,
        classification_2: this.region1.classification2Selection
      }
      axios.post(this.serverBaseURL + '/api/v1/associations/bc1c2', payload)
        .then((res) => {
          this.region1.productSeriesSelections = res.data.product_series_selections
          if (this.region1.productSeriesSelections.length > 0) {
            this.region1.btnEnabled3 = true
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    onRegion1FetchAssociations4 (evt) {
      evt.preventDefault()
      this.region1.supplierNameSelection = ''
      const payload = {
        brand: this.region1.brandSelection,
        classification_1: this.region1.classification1Selection,
        classification_2: this.region1.classification2Selection,
        product_series: this.region1.productSeriesSelection
      }
      axios.post(this.serverBaseURL + '/api/v1/associations/bc1c2', payload)
        .then((res) => {
          this.region1.supplierNameSelections = res.data.supplier_name_selections
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    onRegion2FetchAssociations (evt) {
      evt.preventDefault()
      this.region2.classification2Selection = ''
      const payload = {
        classification_1: this.region2.classification1Selection
      }
      axios.post(this.serverBaseURL + '/api/v1/associations/c1c2', payload)
        .then((res) => {
          this.region2.classification2Selections = res.data.classification_2_selections
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    onRegion3FetchAssociations (evt) {
      evt.preventDefault()
      this.region3.classification2Selection = ''
      const payload = {
        brand: this.region3.brandSelection
      }
      axios.post(this.serverBaseURL + '/api/v1/associations/bc2', payload)
        .then((res) => {
          this.region3.classification2Selections = res.data.classification_2_selections
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    async copyText (value) {
      try {
        await navigator.clipboard.writeText(value)
        this.message = '复制成功！'
        this.showMessage = true
      } catch ($error) {
        this.message = '复制失败！'
        this.showMessage = true
      }
    }
  },
  created () {
    console.log(process.env.NODE_ENV)
    console.log(process.env.SERVER_BASE_URL)
    this.listAllBrandSelections()
    this.listAllClassification1Selections()
  }
}
</script>
