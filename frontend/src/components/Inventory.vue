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
            <b-dropdown-header id="dropdown-header-3"><strong>采购辅助分析报表</strong></b-dropdown-header>
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
        <b-table-simple striped hover small id="inventory-table">
          <b-thead>
            <b-tr>
              <b-th scope="col">导入日期</b-th>
              <b-th scope="col">规格编号</b-th>
              <b-th scope="col">起始库存数量</b-th>
              <b-th scope="col">采购数量</b-th>
              <b-th scope="col">采购退货数量</b-th>
              <b-th scope="col">销售数量</b-th>
              <b-th scope="col">销售退货数量</b-th>
              <b-th scope="col">其他变更数量</b-th>
              <b-th scope="col">截止库存数量</b-th>
            </b-tr>
          </b-thead>
          <b-tbody>
            <b-tr v-for="(inventory, index) in inventories" :key="index">
              <b-td>{{ inventory[8] }}</b-td>
              <b-td>{{ inventory[0] }}</b-td>
              <b-td>{{ inventory[1] }}</b-td>
              <b-td>{{ inventory[2] }}</b-td>
              <b-td>{{ inventory[3] }}</b-td>
              <b-td>{{ inventory[4] }}</b-td>
              <b-td>{{ inventory[5] }}</b-td>
              <b-td>{{ inventory[6] }}</b-td>
              <b-td>{{ inventory[7] }}</b-td>
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
      <b-form-group
        label="自定义年月（可选）："
        label-size="sm"
        label-align-sm="right"
        label-cols-sm="4"
      >
        <b-form-input v-model="customDateSelection" placeholder="YYYY-MM"></b-form-input>
      </b-form-group>
      <b-form @submit="onImport" @reset="onCancel">
        <b-form-group>
          <b-form-file
            accept=".csv"
            v-model="uploadCSVFile"
            :state="Boolean(uploadCSVFile)"
            placeholder="请选择UTF-8编码的CSV文件">
          </b-form-file>
        </b-form-group>
        <div id="inventory-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导入</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </div>
      </b-form>
    </b-modal>
    <b-modal ref="exportFileCase1Modal" id="export-file-case1-modal" title="导出销售报表（按分类汇总）" hide-footer>
      <b-form @submit="onExportCase1" @reset="onCancelExportCase1">
        <div id="inventory-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">导出</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </div>
      </b-form>
    </b-modal>
    <b-modal ref="exportFileCase2Modal" id="export-file-case2-modal" title="导出销售报表（按系列汇总）" hide-footer>
      <b-form>
        <b-form>
          <b-card bg-variant="light">
            <b-form-group
              label="起始日期"
              label-size="sm"
              label-align-sm="right"
              label-cols-sm="3"
            >
              <b-form-input v-model="stDateSelection" placeholder="YYYY-MM"></b-form-input>
            </b-form-group>
            <b-form-group
              label="截止日期"
              label-size="sm"
              label-align-sm="right"
              label-cols-sm="3"
            >
              <b-form-input v-model="edDateSelection" placeholder="YYYY-MM"></b-form-input>
            </b-form-group>
            <div id="inventory-table-operate-btn" class="w-100 d-block">
              <b-button variant="dark" @click="onExportCase2">下载</b-button>
              <b-button variant="dark" @click="onCancelExportCase2">取消</b-button>
            </div>
          </b-card>
        </b-form>
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
            <b-form-input v-model="stDateSelection" placeholder="YYYY-MM"></b-form-input>
          </b-form-group>
          <b-form-group
            label="截止日期"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-input v-model="edDateSelection" placeholder="YYYY-MM"></b-form-input>
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
              :data="brandOptions"
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
              :data="classification1Options"
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
              :data="classification2Options"
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
              :data="productSeriesOptions"
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
            <b-form-select v-model="stopStatusSelection" :options="stopStatusOptions"></b-form-select>
          </b-form-group>
          <b-form-group
            label="组合商品?"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-select v-model="isCombinedSelection" :options="isCombinedOptions"></b-form-select>
          </b-form-group>
          <b-form-group
            label="参与统计?"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-select v-model="beAggregatedSelection" :options="beAggregatedOptions"></b-form-select>
          </b-form-group>
          <b-form-group
            label="进口商品?"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-select v-model="isImportSelection" :options="isImportOptions"></b-form-select>
          </b-form-group>
          <b-form-group
            label="供应商名称"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <v-suggest
              :data="supplierNameOptions"
              show-field="supplier-name"
              v-model="supplierNameSelection"
            ></v-suggest>
          </b-form-group>
          <div id="inventory-table-operate-btn" class="w-100 d-block">
            <b-button variant="dark" @click="onPreviewCase3">下载报表</b-button>
            <b-button variant="dark" @click="onCancelExportCase3">取消</b-button>
          </div>
        </b-card>
      </b-form>
    </b-modal>
    <b-modal ref="previewCase3Modal" title="预览销售报表（按单个SKU汇总）" size="xl" hide-footer>
      <b-table-simple striped hover small id="preview-table">
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
            <b-th scope="col">实时可用库存</b-th>
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
      <div id="inventory-table-operate-btn" class="w-100 d-block">
        <b-button variant="dark" @click="onExportCase3">下载报表</b-button>
        <b-button variant="dark" @click="onCancelPreviewCase3">取消</b-button>
      </div>
    </b-modal>
    <b-modal ref="exportFileCase4Modal" id="export-file-case4-modal" title="导出滞销品报表" hide-footer>
      <b-form>
        <b-card bg-variant="light">
          <b-form-group
            label="起始日期"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-input v-model="stDateSelection" placeholder="YYYY-MM"></b-form-input>
          </b-form-group>
          <b-form-group
            label="截止日期"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-input v-model="edDateSelection" placeholder="YYYY-MM"></b-form-input>
          </b-form-group>
          <b-form-group
            label="品牌"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <v-suggest
              :data="brandOptions"
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
              :data="classification1Options"
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
              :data="classification2Options"
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
              :data="productSeriesOptions"
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
            <b-form-select v-model="stopStatusSelection" :options="stopStatusOptions"></b-form-select>
          </b-form-group>
          <b-form-group
            label="组合商品?"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-select v-model="isCombinedSelection" :options="isCombinedOptions"></b-form-select>
          </b-form-group>
          <b-form-group
            label="参与统计?"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-select v-model="beAggregatedSelection" :options="beAggregatedOptions"></b-form-select>
          </b-form-group>
          <b-form-group
            label="进口商品?"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-select v-model="isImportSelection" :options="isImportOptions"></b-form-select>
          </b-form-group>
          <b-form-group
            label="供应商名称"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <v-suggest
              :data="supplierNameOptions"
              show-field="supplier-name"
              v-model="supplierNameSelection"
            ></v-suggest>
          </b-form-group>
          <b-form-group
            label="库销比阈值"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-input v-model="thresholdSSR" type="number" placeholder="4"></b-form-input>
          </b-form-group>
          <b-form-group
            label="断货折算"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-radio-group v-model="reducedBtnOption" :options="reducedBtnOptions"></b-form-radio-group>
          </b-form-group>
          <div id="inventory-table-operate-btn" class="w-100 d-block">
            <b-button variant="dark" @click="onPreviewCase4">预览报表</b-button>
            <b-button variant="dark" @click="onCancelExportCase4">取消</b-button>
          </div>
        </b-card>
      </b-form>
    </b-modal>
    <b-modal ref="previewCase4Modal" title="预览滞销品报表" size="xl" hide-footer>
      <b-table-simple striped hover small id="preview-table">
        <b-thead>
          <b-tr>
            <b-th scope="col">商品编码</b-th>
            <b-th scope="col">规格编码</b-th>
            <b-th scope="col">商品名称</b-th>
            <b-th scope="col">规格名称</b-th>
            <b-th scope="col">起始库存数量</b-th>
            <b-th scope="col">采购数量</b-th>
            <b-th scope="col">销售数量</b-th>
            <b-th scope="col">截止库存数量</b-th>
            <b-th scope="col">实时可用库存</b-th>
            <b-th scope="col">库销比</b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr v-for="(item, index) in previewCase4.previewTable" :key="index">
            <b-td>{{ item.product_code }}</b-td>
            <b-td>{{ item.specification_code }}</b-td>
            <b-td>{{ item.product_name }}</b-td>
            <b-td>{{ item.specification_name }}</b-td>
            <b-td>{{ item.st_inventory_qty }}</b-td>
            <b-td>{{ item.purchase_qty }}</b-td>
            <b-td>{{ item.sale_qty }}</b-td>
            <b-td>{{ item.ed_inventory_qty }}</b-td>
            <b-td>{{ item.jit_inventory }}</b-td>
            <b-td>{{ item.ssr }}</b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
      <div id="inventory-table-operate-btn" class="w-100 d-block">
        <b-button variant="dark" @click="onExportCase4">下载报表</b-button>
        <b-button variant="dark" @click="onCancelPreviewCase4">取消</b-button>
      </div>
    </b-modal>
    <b-modal ref="exportFileCase5Modal" id="export-file-case5-modal" title="导出采购辅助分析报表" hide-footer>
      <b-form>
        <b-card bg-variant="light">
          <b-form-group
            label="供应商"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="5"
          >
            <b-form-select v-model="supplierNameSelection" :options="supplierNameSelections" :select-size="1"></b-form-select>
          </b-form-group>
          <b-form-group
            label="时间段1（月数）"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="5"
          >
            <b-form-input v-model="timeQuantumX" type="number" placeholder="6"></b-form-input>
          </b-form-group>
          <b-form-group
            label="阈值1"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="5"
          >
            <b-form-input v-model="thresholdX" type="number" placeholder="2"></b-form-input>
          </b-form-group>
          <b-form-group
            label="时间段2（月数）"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="5"
          >
            <b-form-input v-model="timeQuantumY" type="number" placeholder="12"></b-form-input>
          </b-form-group>
          <b-form-group
            label="阈值2"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="5"
          >
            <b-form-input v-model="thresholdY" type="number" placeholder="1"></b-form-input>
          </b-form-group>
          <b-form-group
            label="拟定进货（可销月数）"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="5"
          >
            <b-form-input v-model="projectedPurchase" type="number" placeholder="12"></b-form-input>
          </b-form-group>
          <b-form-group
            label="断货折算"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="5"
          >
            <b-form-radio-group v-model="reducedBtnOption" :options="reducedBtnOptions"></b-form-radio-group>
          </b-form-group>
          <b-form-group
            label="STOP状态?"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="5"
          >
            <b-form-select v-model="stopStatusSelection" :options="stopStatusOptions"></b-form-select>
          </b-form-group>
          <b-form-group
            label="参与统计?"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="5"
          >
            <b-form-select v-model="beAggregatedSelection" :options="beAggregatedOptions"></b-form-select>
          </b-form-group>
          <div id="inventory-table-operate-btn" class="w-100 d-block">
            <b-button variant="dark" @click="onPreviewCase5Pattern1">筛选1</b-button>
            <b-button variant="dark" @click="onPreviewCase5Pattern2">筛选2-同供其他</b-button>
            <b-button variant="dark" @click="onCancelExportCase5">取消</b-button>
          </div>
        </b-card>
      </b-form>
    </b-modal>
    <b-modal ref="previewCase5Modal" title="预览采购辅助分析报表" size="xl" hide-footer>
      <b-table-simple striped hover small id="preview-table">
        <b-thead>
          <b-tr>
            <b-th scope="col">商品编码</b-th>
            <b-th scope="col">品牌</b-th>
            <b-th scope="col">商品名称</b-th>
            <b-th scope="col">规格名称</b-th>
            <b-th scope="col">供应商</b-th>
            <b-th scope="col">X个月销量</b-th>
            <b-th scope="col">Y个月销量</b-th>
            <b-th scope="col">库存量</b-th>
            <b-th scope="col">库存/X个月销量</b-th>
            <b-th scope="col">库存/Y个月销量</b-th>
            <b-th scope="col">库存/X个月折算销量</b-th>
            <b-th scope="col">库存/Y个月折算销量</b-th>
            <b-th scope="col">拟定进货量</b-th>
            <b-th scope="col">单个重量/g</b-th>
            <b-th scope="col">小计重量/kg</b-th>
            <b-th scope="col">单个体积/cm³</b-th>
            <b-th scope="col">小计体积/m³</b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr v-for="(item, index) in previewCase5.previewTable" :key="index">
            <b-td>{{ item.product_code }}</b-td>
            <b-td>{{ item.brand }}</b-td>
            <b-td>{{ item.product_name }}</b-td>
            <b-td>{{ item.specification_name }}</b-td>
            <b-td>{{ item.supplier_name }}</b-td>
            <b-td>{{ item.sale_qty_x_months }}</b-td>
            <b-td>{{ item.sale_qty_y_months }}</b-td>
            <b-td>{{ item.inventory }}</b-td>
            <b-td>{{ item.inventory_divided_by_sale_qty_x_months }}</b-td>
            <b-td>{{ item.inventory_divided_by_sale_qty_y_months }}</b-td>
            <b-td>{{ item.inventory_divided_by_reduced_sale_qty_x_months }}</b-td>
            <b-td>{{ item.inventory_divided_by_reduced_sale_qty_y_months }}</b-td>
            <b-td>{{ item.projected_purchase }}</b-td>
            <b-td>{{ item.weight }}</b-td>
            <b-td>{{ item.weight_total }}</b-td>
            <b-td>{{ item.volume }}</b-td>
            <b-td>{{ item.volume_total }}</b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
      <div id="inventory-table-operate-btn" class="w-100 d-block">
        <b-button variant="dark" @click="onExportCase5">下载报表</b-button>
        <b-button variant="dark" @click="onCancelPreviewCase5">取消</b-button>
      </div>
    </b-modal>
    <b-modal ref="exportFileCase6Modal" id="export-file-case6-modal" title="导出体积、重量计算汇总单" hide-footer>
      <b-form>
        <b-form-group>
          <b-form-file
            accept=".csv"
            v-model="uploadCSVFileForCase6"
            :state="Boolean(uploadCSVFileForCase6)"
            placeholder="导入需求表，请选择UTF-8编码的CSV文件">
          </b-form-file>
        </b-form-group>
        <b-table-simple striped hover small id="preview-table">
          <b-thead>
            <b-tr>
              <b-th scope="col">规格编号</b-th>
              <b-th scope="col">商品数量</b-th>
            </b-tr>
          </b-thead>
          <b-tbody>
            <b-tr v-for="(item, index) in demandTable" :key="index">
              <b-td>{{ item.specification_code }}</b-td>
              <b-td>{{ item.quantity }}</b-td>
            </b-tr>
          </b-tbody>
        </b-table-simple>
        <div id="inventory-table-operate-btn" class="w-100 d-block">
          <b-button variant="dark" @click="onImportForCase6">导入</b-button>
          <b-button variant="dark" @click="onPreviewCase6">预览报表</b-button>
          <b-button variant="dark" @click="onCancelExportCase6">取消</b-button>
        </div>
      </b-form>
    </b-modal>
    <b-modal ref="previewCase6Modal" title="预览体积、重量计算汇总单" size="xl" hide-footer>
      <b-table-simple striped hover small id="preview-table">
        <b-thead>
          <b-tr>
            <b-th scope="col">规格编码</b-th>
            <b-th scope="col">商品名称</b-th>
            <b-th scope="col">规格名称</b-th>
            <b-th scope="col">数量</b-th>
            <b-th scope="col">长度/cm</b-th>
            <b-th scope="col">宽度/cm</b-th>
            <b-th scope="col">高度/cm</b-th>
            <b-th scope="col">体积合计/m³</b-th>
            <b-th scope="col">重量/g</b-th>
            <b-th scope="col">重量合计/kg</b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr v-for="(item, index) in previewCase6.previewTable" :key="index">
            <b-td>{{ item.specification_code }}</b-td>
            <b-td>{{ item.product_name }}</b-td>
            <b-td>{{ item.specification_name }}</b-td>
            <b-td>{{ item.quantity }}</b-td>
            <b-td>{{ item.product_length }}</b-td>
            <b-td>{{ item.product_width }}</b-td>
            <b-td>{{ item.product_height }}</b-td>
            <b-td>{{ item.product_volume_total }}</b-td>
            <b-td>{{ item.product_weight }}</b-td>
            <b-td>{{ item.product_weight_total }}</b-td>
          </b-tr>
          <b-tr>
            <b-td></b-td>
            <b-td></b-td>
            <b-td></b-td>
            <b-td>{{ previewCase6.previewSummaryTable.quantity }}</b-td>
            <b-td></b-td>
            <b-td></b-td>
            <b-td></b-td>
            <b-td>{{ previewCase6.previewSummaryTable.product_volume_total }}</b-td>
            <b-td></b-td>
            <b-td>{{ previewCase6.previewSummaryTable.product_weight_total }}</b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
      <div id="inventory-table-operate-btn" class="w-100 d-block">
        <b-button variant="dark" @click="onExportCase6">下载报表</b-button>
        <b-button variant="dark" @click="onCancelPreviewCase6">取消</b-button>
      </div>
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
  margin-top: 10px;
  margin-bottom: 10px;
}

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

#preview-table {
  border: 2px solid black !important;
  font-size: small;
  table-layout: fixed !important;
}

#preview-table tbody tr td {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

#added-skus-table-operate-btn {
  text-align: right;
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
      customDateSelection: '',
      stDateSelection: '',
      edDateSelection: '',
      productCodeSelection: '',
      productNameSelection: '',
      specificationCodeSelection: '',
      brandOptions: [],
      brandSelection: '',
      classification1Options: [],
      classification1Selection: '',
      classification2Options: [],
      classification2Selection: '',
      productSeriesOptions: [],
      productSeriesSelection: '',
      // TODO： 支持“全部”选项检索
      stopStatusOptions: [
        { value: '在用', text: '在用' },
        { value: '停用', text: '停用' },
        { value: '全部', text: '全部' }
      ],
      stopStatusSelection: '在用',
      isCombinedOptions: [
        { value: '是', text: '是' },
        { value: '否', text: '否' },
        { value: '全部', text: '全部' }
      ],
      isCombinedSelection: '否',
      beAggregatedOptions: [
        { value: '参与', text: '参与' },
        { value: '不参与', text: '不参与' },
        { value: '全部', text: '全部' }
      ],
      beAggregatedSelection: '参与',
      isImportOptions: [
        { value: '进口品', text: '进口品' },
        { value: '非进口品', text: '非进口品' },
        { value: '全部', text: '全部' }
      ],
      isImportSelection: '全部',
      supplierNameOptions: [],
      supplierNameSelections: [],
      supplierNameSelection: '',
      previewCase3: {
        stDate: '',
        edDate: '',
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
      previewCase4: {
        previewTable: []
      },
      previewCase5: {
        previewTable: []
      },
      previewCase6: {
        previewTable: [],
        previewSummaryTable: []
      },
      timeQuantumX: '6',
      thresholdX: '2',
      timeQuantumY: '12',
      thresholdY: '1',
      projectedPurchase: '12',
      reducedBtnOption: 'open',
      reducedBtnOptions: [
        { text: '开', value: 'open' },
        { text: '关', value: 'close' }
      ],
      thresholdSSR: '4',
      inventories: [],
      shouldOpenSidebar: false,
      addedSkus: [],
      pageOffset: 0,
      uploadCSVFile: null,
      uploadCSVFileForCase6: null,
      demandTable: [],
      message: '',
      showMessage: false
    }
  },
  components: {
    alert: Alert,
    'v-suggest': Suggest
  },
  methods: {
    listAllOptions () {
      axios.get(this.serverBaseURL + '/api/v1/alloptions')
        .then((res) => {
          this.brandOptions = res.data.brand_options
          this.classification1Options = res.data.classification_1_options
          this.classification2Options = res.data.classification_2_options
          this.productSeriesOptions = res.data.product_series_options
          this.supplierNameOptions = res.data.supplier_name_options
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误!'
          this.showMessage = true
        })
    },
    listAllSupplierSelections () {
      axios.get(this.serverBaseURL + '/api/v1/allselections/suppliers')
        .then((res) => {
          this.supplierNameSelections = res.data.supplier_name_selections
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
      this.setDefaultDate()
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
      this.isImportSelection = '全部'
      this.supplierNameSelection = ''
      this.previewCase3.stDate = ''
      this.previewCase3.edDate = ''
      this.previewCase3.productCode = ''
      this.previewCase3.specificationCode = ''
      this.previewCase3.productName = ''
      this.previewCase3.specificationName = ''
      this.previewCase3.stInventoryQty = 0
      this.previewCase3.purchaseQty = 0
      this.previewCase3.saleQty = 0
      this.previewCase3.edInventoryQty = 0
      this.previewCase3.jitInventory = 0
      this.previewCase4.previewTable = []
      this.previewCase5.previewTable = []
      this.previewCase6.previewTable = []
      this.previewCase6.previewSummaryTable = []
      this.timeQuantumX = '6'
      this.thresholdX = '2'
      this.timeQuantumY = '12'
      this.thresholdY = '1'
      this.projectedPurchase = '12'
      this.reducedBtnOption = 'open'
      this.thresholdSSR = '4'
    },
    importCSVFile (formData, date) {
      let config = {
        header: {
          'Content-Type': 'multipart/form-data'
        }
      }
      axios.post(this.serverBaseURL + '/api/v1/inventories/upload', formData, config, date)
        .then((res) => {
          if (res.data.status === 'success') {
            this.listInventories()
            this.message = date + '数据导入成功!'
            this.showMessage = true
          } else if (res.data.status === 'repetition') {
            this.message = '导入失败! 数据表格重复导入！'
            this.showMessage = true
          } else if (res.data.status === 'new SKUs') {
            this.message = '禁止导入，有新增SKU！'
            this.showMessage = true
            this.addedSkus = res.data.added_skus
            this.shouldOpenSidebar = true
          } else {
            this.message = '导入失败! 数据表格格式有变更，请人工复合！'
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
    onImport (evt) {
      evt.preventDefault()
      this.$refs.importCSVFileModal.hide()
      let formData = new FormData()
      formData.append('file', this.uploadCSVFile, this.uploadCSVFile.name)
      formData.append('import_date', this.customDateSelection)
      this.importCSVFile(formData, this.customDateSelection)
      this.setDefaultDate()
      this.uploadCSVFile = null
    },
    onCancel (evt) {
      evt.preventDefault()
      this.$refs.importCSVFileModal.hide()
      this.setDefaultDate()
      this.uploadCSVFile = null
    },
    // 销售报表（按分类汇总）
    onExportCase1 (evt) {
      // 确定导出销售报表（按分类汇总）
      evt.preventDefault()
      this.$refs.exportFileCase1Modal.hide()
      const payload = {}
      this.exportReportFileCase1(payload)
      this.initExportForm()
    },
    onCancelExportCase1 (evt) {
      // 取消导出销售报表（按分类汇总）
      evt.preventDefault()
      this.$refs.exportFileCase1Modal.hide()
      this.initExportForm()
    },
    // 销售报表（按系列汇总）
    onExportCase2 (evt) {
      // 确定导出销售报表（按系列汇总）
      evt.preventDefault()
      this.$refs.exportFileCase2Modal.hide()
      const payload = {
        st_date: this.stDateSelection,
        ed_date: this.edDateSelection
      }
      this.prepareExportReportFile('/api/v1/case2/prepare', payload)
      this.initExportForm()
    },
    onCancelExportCase2 (evt) {
      // 取消导出销售报表（按系列汇总）
      evt.preventDefault()
      this.$refs.exportFileCase2Modal.hide()
      this.initExportForm()
    },
    // 销售报表（按单个SKU汇总）
    previewReportFileCase3 (payload) {
      axios.post(this.serverBaseURL + '/api/v1/case3/preview', payload)
        .then((res) => {
          if (res.data.status === 'success') {
            this.previewCase3.stDate = res.data.st_date
            this.previewCase3.edDate = res.data.ed_date
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
        this.previewReportFileCase3(payload)
      }
      this.initExportForm()
    },
    onCancelPreviewCase3 (evt) {
      evt.preventDefault()
      this.$refs.previewCase3Modal.hide()
      this.initExportForm()
    },
    onExportCase3 (evt) {
      // 确定下载销售报表（按单个SKU汇总）
      evt.preventDefault()
      this.$refs.previewCase3Modal.hide()
      this.$refs.exportFileCase3Modal.hide()
      const payload = {
        st_date: this.previewCase3.stDate,
        ed_date: this.previewCase3.edDate,
        specification_code: this.previewCase3.specificationCode
      }
      this.prepareExportReportFile('/api/v1/case3/prepare', payload)
      this.initExportForm()
    },
    onCancelExportCase3 (evt) {
      // 取消下载销售报表（按单个SKU汇总）
      evt.preventDefault()
      this.$refs.exportFileCase3Modal.hide()
      this.initExportForm()
    },
    // 滞销品报表
    onExportCase4 (evt) {
      // 确定导出滞销品报表
      evt.preventDefault()
      this.$refs.previewCase4Modal.hide()
      this.$refs.exportFileCase4Modal.hide()
      const payload = {
        preview_table: this.previewCase4.previewTable
      }
      this.prepareExportReportFile('/api/v1/case4/prepare', payload)
      this.initExportForm()
    },
    previewReportFileCase4 (payload) {
      axios.post(this.serverBaseURL + '/api/v1/case4/preview', payload)
        .then((res) => {
          if (res.data.status === 'success') {
            this.previewCase4.previewTable = res.data.preview_table
            this.$refs.previewCase4Modal.show()
          } else {
            this.message = '预览失败! 不存在指定的库存条目.'
            this.showMessage = true
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '预览失败!'
          this.showMessage = true
        })
    },
    onPreviewCase4 (evt) {
      evt.preventDefault()
      if ((this.stDateSelection === '') || (this.edDateSelection === '')) {
        this.message = '起始日期/截止日期不能为空!'
        this.showMessage = true
      } else {
        const payload = {
          st_date: this.stDateSelection,
          ed_date: this.edDateSelection,
          brand: this.brandSelection,
          classification_1: this.classification1Selection,
          classification_2: this.classification2Selection,
          product_series: this.productSeriesSelection,
          stop_status: this.stopStatusSelection,
          is_combined: this.isCombinedSelection,
          be_aggregated: this.beAggregatedSelection,
          is_import: this.isImportSelection,
          supplier_name: this.supplierNameSelection,
          threshold_ssr: this.thresholdSSR,
          reduced_btn_option: this.reducedBtnOption
        }
        this.previewReportFileCase4(payload)
      }
    },
    onCancelPreviewCase4 (evt) {
      evt.preventDefault()
      this.$refs.previewCase4Modal.hide()
      this.initExportForm()
    },
    onCancelExportCase4 (evt) {
      // 取消导出滞销品报表
      evt.preventDefault()
      this.$refs.exportFileCase4Modal.hide()
      this.initExportForm()
    },
    // 采购辅助分析报表
    previewReportFileCase5Way (url, payload) {
      axios.post(this.serverBaseURL + url, payload)
        .then((res) => {
          if (res.data.status === 'success') {
            this.previewCase5.previewTable = res.data.preview_table
            this.$refs.previewCase5Modal.show()
          } else {
            this.message = '预览失败! 不存在指定的库存条目.'
            this.showMessage = true
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '预览失败!'
          this.showMessage = true
        })
    },
    onPreviewCase5Pattern1 (evt) {
      evt.preventDefault()
      const payload = {
        supplier_name: this.supplierNameSelection,
        time_quantum_x: this.timeQuantumX,
        threshold_x: this.thresholdX,
        time_quantum_y: this.timeQuantumY,
        threshold_y: this.thresholdY,
        projected_purchase: this.projectedPurchase,
        reduced_btn_option: this.reducedBtnOption,
        stop_status: this.stopStatusSelection,
        be_aggregated: this.beAggregatedSelection
      }
      this.previewReportFileCase5Way('/api/v1/case5/preview?way=1', payload)
    },
    onPreviewCase5Pattern2 (evt) {
      evt.preventDefault()
      const payload = {
        supplier_name: this.supplierNameSelection,
        time_quantum_x: this.timeQuantumX,
        threshold_x: this.thresholdX,
        time_quantum_y: this.timeQuantumY,
        threshold_y: this.thresholdY,
        projected_purchase: this.projectedPurchase,
        reduced_btn_option: this.reducedBtnOption,
        stop_status: this.stopStatusSelection,
        be_aggregated: this.beAggregatedSelection
      }
      this.previewReportFileCase5Way('/api/v1/case5/preview?way=2', payload)
    },
    onCancelPreviewCase5 (evt) {
      evt.preventDefault()
      this.$refs.previewCase5Modal.hide()
      this.initExportForm()
    },
    onExportCase5 (evt) {
      // 确定导出采购辅助分析报表
      evt.preventDefault()
      this.$refs.previewCase5Modal.hide()
      this.$refs.exportFileCase5Modal.hide()
      const payload = {
        preview_table: this.previewCase5.previewTable
      }
      this.prepareExportReportFile('/api/v1/case5/prepare', payload)
      this.initExportForm()
    },
    onCancelExportCase5 (evt) {
      // 取消导出采购辅助分析报表
      evt.preventDefault()
      this.$refs.exportFileCase5Modal.hide()
      this.initExportForm()
    },
    // 体积、重量计算汇总单
    onImportForCase6 (evt) {
      evt.preventDefault()
      let formData = new FormData()
      formData.append('file', this.uploadCSVFileForCase6, this.uploadCSVFileForCase6.name)
      this.importCSVFileForCase6(formData)
    },
    onCancelExportCase6 (evt) {
      evt.preventDefault()
      this.$refs.exportFileCase6Modal.hide()
      this.uploadCSVFileForCase6 = null
      this.demandTable = []
    },
    importCSVFileForCase6 (formData) {
      let config = {
        header: {
          'Content-Type': 'multipart/form-data'
        }
      }
      axios.post(this.serverBaseURL + '/api/v1/case6/upload', formData, config)
        .then((res) => {
          this.message = '导入成功!'
          this.showMessage = true
          this.demandTable = res.data.demand_table
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '导入失败!'
          this.showMessage = true
        })
    },
    onPreviewCase6 (evt) {
      evt.preventDefault()
      if (this.demandTable.length === 0) {
        this.message = '请先加载需求表!'
        this.showMessage = true
      } else {
        const payload = {
          demand_table: this.demandTable
        }
        this.previewReportFileCase6(payload)
      }
    },
    previewReportFileCase6 (payload) {
      axios.post(this.serverBaseURL + '/api/v1/case6/preview', payload)
        .then((res) => {
          if (res.data.status === 'success') {
            this.previewCase6.previewTable = res.data.preview_table
            this.previewCase6.previewSummaryTable = res.data.preview_summary_table
            this.$refs.previewCase6Modal.show()
          } else {
            this.message = '预览失败! 不存在指定的商品条目.'
            this.showMessage = true
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '预览失败!'
          this.showMessage = true
        })
    },
    onExportCase6 (evt) {
      // 确定下载体积、重量计算汇总单
      evt.preventDefault()
      this.$refs.previewCase6Modal.hide()
      this.$refs.exportFileCase6Modal.hide()
      const payload = {
        preview_table: this.previewCase6.previewTable,
        preview_summary_table: this.previewCase6.previewSummaryTable
      }
      this.prepareExportReportFile('/api/v1/case6/prepare', payload)
      this.initExportForm()
    },
    onCancelPreviewCase6 (evt) {
      evt.preventDefault()
      this.$refs.previewCase6Modal.hide()
      this.initExportForm()
    },
    prepareExportReportFile (url, payload) {
      this.$refs.processingModal.show()
      axios.post(this.serverBaseURL + url, payload)
        .then((res) => {
          this.exportReportFile(res.data.server_send_queue_file, res.data.output_file)
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '下载失败!'
          this.showMessage = true
        })
    },
    exportReportFile (queryFile, saveFile) {
      axios.get(this.serverBaseURL + '/api/v1/download/' + queryFile)
        .then((res) => {
          this.$refs.processingModal.hide()
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
          this.$refs.processingModal.hide()
          // eslint-disable-next-line
          console.log(error)
          this.message = '下载失败!'
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
    onPrevPage (evt) {
      evt.preventDefault()
      this.pageOffset -= 20
      this.listInventories()
    },
    onNextPage (evt) {
      evt.preventDefault()
      this.pageOffset += 20
      this.listInventories()
    },
    setDefaultDate () {
      var today = new Date()
      var year = today.getFullYear() * 1
      var month = today.getMonth() * 1 + 1
      // 为导入时间设置默认值
      if (month >= 10) {
        this.customDateSelection = year.toString() + '-' + month.toString()
      } else {
        this.customDateSelection = year.toString() + '-0' + month.toString()
      }
      // 为起始时间设置默认值
      var stYear
      var stMonth
      if (month - 3 < 0) {
        stYear = year - 1
        stMonth = month - 3 + 12
      } else {
        stYear = year
        stMonth = month - 3
      }
      if (stMonth >= 10) {
        this.stDateSelection = stYear.toString() + '-' + stMonth.toString()
      } else {
        this.stDateSelection = stYear.toString() + '-0' + stMonth.toString()
      }
      // 为截止时间设置默认值
      var edYear
      var edMonth
      if (month - 1 < 0) {
        edYear = year - 1
        edMonth = month - 1 + 12
      } else {
        edYear = year
        edMonth = month - 1
      }
      if (edMonth >= 10) {
        this.edDateSelection = edYear.toString() + '-' + edMonth.toString()
      } else {
        this.edDateSelection = edYear.toString() + '-0' + edMonth.toString()
      }
    }
  },
  created () {
    console.log(process.env.NODE_ENV)
    console.log(process.env.SERVER_BASE_URL)
    this.listAllOptions()
    this.listAllSupplierSelections()
    this.listInventories()
    this.setDefaultDate()
  }
}
</script>
