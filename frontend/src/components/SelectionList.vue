<template>
  <div class="container-fluid">
    <navbar></navbar>
    <br/>
    <alert :message=message v-if="showMessage"></alert>
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
import Navbar from './Navbar.vue'
import router from '../router'

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
    alert: Alert,
    navbar: Navbar
  },
  methods: {
    async listAllBrandSelections () {
      await axios.get(this.serverBaseURL + '/api/v1/selections/brands')
        .then((res) => {
          const bss = Object.freeze(res.data.brand_selections)
          this.region1.brandSelections = bss
          this.region3.brandSelections = bss
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
    async listAllClassification1Selections () {
      await axios.get(this.serverBaseURL + '/api/v1/selections/classification1')
        .then((res) => {
          const c1ss = Object.freeze(res.data.classification_1_selections)
          this.region2.classification1Selections = c1ss
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
    async onRegion1FetchAssociations1 (evt) {
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
      await axios.post(this.serverBaseURL + '/api/v1/associations/bc1c2', payload)
        .then((res) => {
          const c1ss = Object.freeze(res.data.classification_1_selections)
          this.region1.classification1Selections = c1ss
          if (this.region1.classification1Selections.length > 0) {
            this.region1.btnEnabled1 = true
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
    async onRegion1FetchAssociations2 (evt) {
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
      await axios.post(this.serverBaseURL + '/api/v1/associations/bc1c2', payload)
        .then((res) => {
          const c2ss = Object.freeze(res.data.classification_2_selections)
          this.region1.classification2Selections = c2ss
          if (this.region1.classification2Selections.length > 0) {
            this.region1.btnEnabled2 = true
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
    async onRegion1FetchAssociations3 (evt) {
      evt.preventDefault()
      this.region1.btnEnabled3 = false
      this.region1.productSeriesSelection = ''
      this.region1.supplierNameSelection = ''
      const payload = {
        brand: this.region1.brandSelection,
        classification_1: this.region1.classification1Selection,
        classification_2: this.region1.classification2Selection
      }
      await axios.post(this.serverBaseURL + '/api/v1/associations/bc1c2', payload)
        .then((res) => {
          const psss = Object.freeze(res.data.product_series_selections)
          this.region1.productSeriesSelections = psss
          if (this.region1.productSeriesSelections.length > 0) {
            this.region1.btnEnabled3 = true
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
    async onRegion1FetchAssociations4 (evt) {
      evt.preventDefault()
      this.region1.supplierNameSelection = ''
      const payload = {
        brand: this.region1.brandSelection,
        classification_1: this.region1.classification1Selection,
        classification_2: this.region1.classification2Selection,
        product_series: this.region1.productSeriesSelection
      }
      await axios.post(this.serverBaseURL + '/api/v1/associations/bc1c2', payload)
        .then((res) => {
          const snss = Object.freeze(res.data.supplier_name_selections)
          this.region1.supplierNameSelections = snss
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
    async onRegion2FetchAssociations (evt) {
      evt.preventDefault()
      this.region2.classification2Selection = ''
      const payload = {
        classification_1: this.region2.classification1Selection
      }
      await axios.post(this.serverBaseURL + '/api/v1/associations/c1c2', payload)
        .then((res) => {
          const c2ss = Object.freeze(res.data.classification_2_selections)
          this.region2.classification2Selections = c2ss
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
    async onRegion3FetchAssociations (evt) {
      evt.preventDefault()
      this.region3.classification2Selection = ''
      const payload = {
        brand: this.region3.brandSelection
      }
      await axios.post(this.serverBaseURL + '/api/v1/associations/bc2', payload)
        .then((res) => {
          const c2ss = Object.freeze(res.data.classification_2_selections)
          this.region3.classification2Selections = c2ss
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

    if (this.$cookies.isKey('logged')) {
      if (this.$cookies.get('logged') === 'in') {
        this.listAllBrandSelections()
        this.listAllClassification1Selections()
      } else {
        router.push('/login')
      }
    } else {
      router.push('/login')
    }
  }
}
</script>
