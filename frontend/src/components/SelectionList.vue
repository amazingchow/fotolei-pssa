<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-3">
      </div>
      <div class="col-sm-6">
        <h1>搜索项列表</h1>
        <hr>
        <b-card bg-variant="light">
          <b-form-group
            label="品牌"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="2"
          >
            <b-form-select :options="brandSelections" :select-size="1"></b-form-select>
          </b-form-group>
          <b-form-group
            label="分类1"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="2"
          >
            <b-form-select :options="classification1Selections" :select-size="1"></b-form-select>
          </b-form-group>
          <b-form-group
            label="分类2"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="2"
          >
            <b-form-select :options="classification2Selections" :select-size="1"></b-form-select>
          </b-form-group>
          <b-form-group
            label="产品系列"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="2"
          >
            <b-form-select :options="productSeriesSelections" :select-size="1"></b-form-select>
          </b-form-group>
          <b-form-group
            label="供应商名称"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="2"
          >
            <b-form-select :options="supplierNameSelections" :select-size="1"></b-form-select>
          </b-form-group>
        </b-card>
      </div>
      <div class="col-sm-3">
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      serverBaseURL: process.env.SERVER_BASE_URL,
      brandSelections: [],
      classification1Selections: [],
      classification2Selections: [],
      productSeriesSelections: [],
      supplierNameSelections: []
    }
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
    }
  },
  created () {
    console.log(process.env.NODE_ENV)
    console.log(process.env.SERVER_BASE_URL)
    this.listAllSelections()
  }
}
</script>
