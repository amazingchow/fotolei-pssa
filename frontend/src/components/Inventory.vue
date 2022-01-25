<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-sm-12">
        <b-navbar type="dark" variant="dark">
          <b-navbar-nav>
            <b-nav-item :active="false" href="/product">商品明细库</b-nav-item>
            <b-nav-item :active="true" href="/">库存明细库</b-nav-item>
            <b-nav-item :active="false" href="/slist">辅助查询</b-nav-item>
            <b-nav-item :active="false" href="/oplog">操作日志</b-nav-item>
          </b-navbar-nav>
        </b-navbar>
      </div>
    </div>
    <br/>
    <div class="row">
      <div class="col-sm-12">
        <alert :message=message v-if="showMessage"></alert>
        <div id="import-and-export-btn-area">
          <button type="button" class="btn btn-secondary btn-sm" v-b-modal.csv-file-modal>导入库存数据</button>
          <button type="button" class="btn btn-secondary btn-sm" v-b-modal.inventories-clean-all-modal>删除库存明细</button>
          <b-dropdown text="导出定制报表" variant="secondary" size="sm">
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
              <b-th scope="col">规格编码</b-th>
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
          <b-tfoot id="inventory-table-footer">
            <b-tr>
              <b-td colspan="9" variant="secondary">总共录入<b>{{ inventoriesTotal }}</b>条记录，共计<b>{{ pageTotal }}</b>页，当前展示第<b>{{ pageCurr }}</b>页，共<b>{{ inventoriesNum }}</b>条记录</b-td>
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
    <b-modal ref="CleanAllInventoriesModal" id="inventories-clean-all-modal" title="删除全量库存明细" hide-footer>
      <b-form @submit="onCleanAllInventories" @reset="onCancelCleanAllInventories">
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
        <div id="inventory-table-operate-btn" class="w-100 d-block">
          <b-button type="submit" variant="dark">删除</b-button>
          <b-button type="reset" variant="dark">取消</b-button>
        </div>
      </b-form>
    </b-modal>
    <b-modal ref="exportFileCase1Modal" id="export-file-case1-modal" title="导出销售报表（按分类汇总）" hide-footer>
      <b-form>
        <b-form>
          <b-card bg-variant="light">
            <b-form-group
              label="起始日期"
              label-size="sm"
              label-align-sm="right"
              label-cols-sm="3"
            >
              <b-form-input v-model="stDateSelectionForCase1" placeholder="YYYY-MM"></b-form-input>
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
              <b-button variant="dark" @click="onCustomizeCase1">自定义报表</b-button>
              <b-button variant="dark" @click="onPreviewCase1">预览报表</b-button>
              <b-button variant="dark" @click="onCancelExportCase1">取消</b-button>
            </div>
          </b-card>
        </b-form>
      </b-form>
    </b-modal>
    <b-modal ref="previewCase1Modal" title="预览销售报表（按分类汇总）" size="xl" hide-footer>
      <b-table-simple striped hover small id="preview-table">
        <b-tbody>
          <b-tr v-for="(item, index) in previewCase1.previewTable" :key="index">
            <b-td>{{ item[0] }}</b-td>
            <b-td>{{ item[1] }}</b-td>
            <b-td>{{ item[2] }}</b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
      <div id="inventory-table-operate-btn" class="w-100 d-block">
        <b-button variant="dark" @click="onExportCase1">下载报表</b-button>
        <b-button variant="dark" @click="onCancelPreviewCase1">取消</b-button>
      </div>
    </b-modal>
    <b-modal ref="customizeCase1Modal" id="customize-case1-modal" title="自定义销售报表（按分类汇总）样式" size="huge" hide-footer>
      <b-form>
        <b-form>
          <b-card bg-variant="light">
            <b-form-group
              label="参与统计的'分类1'"
              label-size="sm"
              label-align-sm="right"
              label-cols-sm="2"
            >
              <b-form-tags
                v-model="customizeCase1.classification1_tags"
                separator=" "
                placeholder="输入标签（空格键确定）"
                remove-on-delete
                no-add-on-enter
              ></b-form-tags>
            </b-form-group>
            <b-form-group
              label="参与统计的'分类1|分类2'"
              label-size="sm"
              label-align-sm="right"
              label-cols-sm="2"
            >
              <b-form-tags
                v-model="customizeCase1.classification1_classification2_tags"
                separator=" "
                placeholder="输入标签（空格键确定）"
                remove-on-delete
                no-add-on-enter
              ></b-form-tags>
            </b-form-group>
            <b-form-group
              label="销售top必选（分类1）"
              label-size="sm"
              label-align-sm="right"
              label-cols-sm="2"
            >
              <b-form-tags
                v-model="customizeCase1.classification1_topk_tags"
                separator=" "
                placeholder="输入标签（空格键确定）"
                remove-on-delete
                no-add-on-enter
              ></b-form-tags>
            </b-form-group>
            <b-form-group
              label="参与统计的品牌"
              label-size="sm"
              label-align-sm="right"
              label-cols-sm="2"
            >
              <b-form-tags
                v-model="customizeCase1.brand_tags"
                separator=" "
                placeholder="输入标签（空格键确定）"
                remove-on-delete
                no-add-on-enter
              ></b-form-tags>
            </b-form-group>
            <b-form-group
              label="销售top必选（品牌）"
              label-size="sm"
              label-align-sm="right"
              label-cols-sm="2"
            >
              <b-form-input
                v-model="customizeCase1.brand_topk_tag"
              ></b-form-input>
            </b-form-group>
            <b-form-group
              label="参与统计的'品牌|分类2'"
              label-size="sm"
              label-align-sm="right"
              label-cols-sm="2"
            >
              <b-form-tags
                v-model="customizeCase1.brand_classification2_tags"
                separator=" "
                placeholder="输入标签（空格键确定）"
                remove-on-delete
                no-add-on-enter
              ></b-form-tags>
            </b-form-group>
            <div id="inventory-table-operate-btn" class="w-100 d-block">
              <b-button variant="dark" @click="onSaveCustomizeCase1">保存</b-button>
              <b-button variant="dark" @click="onCancelSaveCustomizeCase1">取消</b-button>
            </div>
          </b-card>
        </b-form>
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
              <b-button variant="dark" @click="onPreviewCase2">预览报表</b-button>
              <b-button variant="dark" @click="onCancelExportCase2">取消</b-button>
            </div>
          </b-card>
        </b-form>
      </b-form>
    </b-modal>
    <b-modal ref="previewCase2Modal" title="预览销售报表（按系列汇总）" size="huge" hide-footer>
      <b-table-simple striped hover small id="preview-table">
        <b-thead>
          <b-tr>
            <b-th scope="col">产品系列</b-th>
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
            <b-th scope="col">实时可用库存</b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr v-for="(item, index) in previewCase2.previewTable" :key="index">
            <b-td>{{ item.product_series }}</b-td>
            <b-td>{{ item.st_inventory_qty }}</b-td>
            <b-td>{{ item.st_inventory_total }}</b-td>
            <b-td>{{ item.purchase_qty }}</b-td>
            <b-td>{{ item.purchase_total }}</b-td>
            <b-td>{{ item.purchase_then_return_qty }}</b-td>
            <b-td>{{ item.purchase_then_return_total }}</b-td>
            <b-td>{{ item.sale_qty }}</b-td>
            <b-td>{{ item.sale_total }}</b-td>
            <b-td>{{ item.sale_then_return_qty }}</b-td>
            <b-td>{{ item.sale_then_return_total }}</b-td>
            <b-td>{{ item.others_qty }}</b-td>
            <b-td>{{ item.others_total }}</b-td>
            <b-td>{{ item.ed_inventory_qty }}</b-td>
            <b-td>{{ item.ed_inventory_total }}</b-td>
            <b-td>{{ item.jit_inventory }}</b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
      <div id="inventory-table-operate-btn" class="w-100 d-block">
        <b-button variant="dark" @click="onExportCase2">下载报表</b-button>
        <b-button variant="dark" @click="onCancelPreviewCase2">取消</b-button>
      </div>
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
            <b-button variant="dark" @click="onPreviewCase3">预览报表</b-button>
            <b-button variant="dark" @click="onCancelExportCase3">取消</b-button>
          </div>
        </b-card>
      </b-form>
    </b-modal>
    <b-modal ref="previewCase3Modal" title="预览销售报表（按单个SKU汇总）" size="xl" hide-footer>
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
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr v-for="(item, index) in previewCase3.previewTable" :key="index">
            <b-td>{{ item.product_code }}</b-td>
            <b-td>{{ item.specification_code }}</b-td>
            <b-td>{{ item.product_name }}</b-td>
            <b-td>{{ item.specification_name }}</b-td>
            <b-td>{{ item.st_inventory_qty }}</b-td>
            <b-td>{{ item.purchase_qty }}</b-td>
            <b-td>{{ item.sale_qty }}</b-td>
            <b-td>{{ item.ed_inventory_qty }}</b-td>
            <b-td>{{ item.jit_inventory }}</b-td>
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
            <b-form-input v-model="thresholdSSR" type="number" min="0" step="1" placeholder="4"></b-form-input>
          </b-form-group>
          <b-form-group
            label="断货折算"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="3"
          >
            <b-form-checkbox v-model="reducedBtnOption" switch></b-form-checkbox>
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
            <b-th scope="col">销售退货数量</b-th>
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
            <b-td>{{ item.sale_then_return_qty }}</b-td>
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
            <b-form-input v-model="timeQuantumX" type="number" min="0" step="1" placeholder="6"></b-form-input>
          </b-form-group>
          <b-form-group
            label="阈值1"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="5"
          >
            <b-form-input v-model="thresholdX" type="number" min="0" step="1" placeholder="2"></b-form-input>
          </b-form-group>
          <b-form-group
            label="时间段2（月数）"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="5"
          >
            <b-form-input v-model="timeQuantumY" type="number" min="0" step="1" placeholder="12"></b-form-input>
          </b-form-group>
          <b-form-group
            label="阈值2"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="5"
          >
            <b-form-input v-model="thresholdY" type="number" min="0" step="1" placeholder="1"></b-form-input>
          </b-form-group>
          <b-form-group
            label="拟定进货（可销月数）"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="5"
          >
            <b-form-input v-model="projectedPurchase" type="number" min="0" step="1" placeholder="12"></b-form-input>
          </b-form-group>
          <b-form-group
            label="断货折算"
            label-size="sm"
            label-align-sm="right"
            label-cols-sm="5"
          >
            <b-form-checkbox v-model="reducedBtnOption" switch></b-form-checkbox>
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
    <b-modal ref="previewCase5Modal" title="预览采购辅助分析报表" size="huge" hide-footer>
      <b-table-simple striped hover small id="preview-table">
        <b-thead>
          <b-tr>
            <b-th scope="col">规格编码</b-th>
            <b-th scope="col">品牌</b-th>
            <b-th scope="col">商品名称</b-th>
            <b-th scope="col">规格名称</b-th>
            <b-th scope="col">采购名称</b-th>
            <b-th scope="col">供应商</b-th>
            <b-th scope="col">{{ timeQuantumX }}个月销量</b-th>
            <b-th scope="col">{{ timeQuantumY }}个月销量</b-th>
            <b-th scope="col">库存量</b-th>
            <b-th scope="col">库存/{{ timeQuantumX }}个月销量</b-th>
            <b-th scope="col">库存/{{ timeQuantumY }}个月销量</b-th>
            <b-th scope="col">库存/{{ timeQuantumX }}个月折算销量</b-th>
            <b-th scope="col">库存/{{ timeQuantumY }}个月折算销量</b-th>
            <b-th scope="col">拟定进货量</b-th>
            <b-th scope="col">单个重量/g</b-th>
            <b-th scope="col">小计重量/kg</b-th>
            <b-th scope="col">单个体积/cm³</b-th>
            <b-th scope="col">小计体积/m³</b-th>
            <b-th scope="col">备注</b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr v-for="(item, index) in previewCase5.previewTable" :key="index">
            <b-td>{{ item.specification_code }}</b-td>
            <b-td>{{ item.brand }}</b-td>
            <b-td>{{ item.product_name }}</b-td>
            <b-td>{{ item.specification_name }}</b-td>
            <b-td>{{ item.purchase_name }}</b-td>
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
            <b-td>{{ item.remark }}</b-td>
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
              <b-th scope="col">规格编码</b-th>
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

@media (min-width: 992px) {
  .modal .modal-huge {
    width: 90% !important;;
    max-width: 90% !important;
  }
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
      dateReg: /^20[1-3][0-9]-(0[1-9]|1[0-2])$/,
      adminUsr: '',
      adminPwd: '',
      customDateSelection: '',
      stDateSelectionForCase1: '',
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
      customizeCase1: {
        classification1_tags: [],
        classification1_classification2_tags: [],
        classification1_topk_tags: [],
        brand_tags: [],
        brand_topk_tag: '',
        brand_classification2_tags: []
      },
      previewCase1: {
        previewTable: []
      },
      previewCase2: {
        previewTable: []
      },
      previewCase3: {
        previewTable: []
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
      supplierNameListFromScreeningWay1: [],
      timeQuantumX: '6',
      thresholdX: '2',
      timeQuantumY: '12',
      thresholdY: '1',
      projectedPurchase: '12',
      reducedBtnOption: true,
      thresholdSSR: '4',
      inventories: [],
      inventoriesNum: 0,
      inventoriesTotal: 0,
      shouldOpenSidebar: false,
      addedSkus: [],
      pageJump: 1,
      pageCurr: 0,
      pageTotal: 0,
      pageOffset: 0,
      pageOffsetMax: 0,
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
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    listAllSupplierSelections () {
      axios.get(this.serverBaseURL + '/api/v1/suppliers')
        .then((res) => {
          this.supplierNameSelections = res.data.supplier_name_selections
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    listInventories () {
      axios.get(this.serverBaseURL + `/api/v1/inventories?page.offset=${this.pageOffset}&page.limit=20`)
        .then((res) => {
          this.inventories = res.data.inventories
          this.inventoriesNum = res.data.inventories.length
          if (this.inventoriesNum > 0) {
            this.pageCurr = this.pageOffset / 20 + 1
          } else {
            this.pageCurr = 0
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
          this.showMessage = true
        })
    },
    getInventoriesTotal () {
      axios.get(this.serverBaseURL + '/api/v1/inventories/total')
        .then((res) => {
          this.inventoriesTotal = res.data.inventories_total
          this.pageOffsetMax = this.inventoriesTotal - this.inventoriesTotal % 20
          if (this.inventoriesTotal > 0) {
            this.pageTotal = this.pageOffsetMax / 20 + 1
          } else {
            this.pageTotal = 0
          }
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '内部服务错误！'
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
      this.previewCase1.previewTable = []
      this.previewCase2.previewTable = []
      this.previewCase3.previewTable = []
      this.previewCase4.previewTable = []
      this.previewCase5.previewTable = []
      this.previewCase6.previewTable = []
      this.previewCase6.previewSummaryTable = []
      this.supplierNameListFromScreeningWay1 = []
      this.timeQuantumX = '6'
      this.thresholdX = '2'
      this.timeQuantumY = '12'
      this.thresholdY = '1'
      this.projectedPurchase = '12'
      this.reducedBtnOption = true
      this.thresholdSSR = '4'
      this.uploadCSVFileForCase6 = null
      this.demandTable = null
    },
    importCSVFileClose () {
      this.$refs.processingModal.hide()
      this.setDefaultDate()
      this.uploadCSVFile = null
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
            this.getInventoriesTotal()
            if (res.data.msg.length > 0) {
              this.message = date + '数据导入成功！' + res.data.msg
            } else {
              this.message = date + '数据导入成功！'
            }
            this.showMessage = true
          } else if (res.data.status === 'repetition') {
            this.message = '导入失败！数据表格重复导入！'
            this.showMessage = true
          } else if (res.data.status === 'new SKUs') {
            this.message = '禁止导入，有新增SKU！'
            this.showMessage = true
            this.addedSkus = res.data.added_skus
            this.shouldOpenSidebar = true
          } else if (res.data.status === 'invalid input data') {
            this.message = '导入失败！' + res.data.err_msg
            this.showMessage = true
          } else {
            this.message = '导入失败！数据表格格式有变更，请人工复合！'
            this.showMessage = true
          }
          this.importCSVFileClose()
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '导入失败！'
          this.showMessage = true
          this.importCSVFileClose()
        })
    },
    onImport (evt) {
      evt.preventDefault()
      if (this.dateReg.test(this.customDateSelection)) {
        if (this.uploadCSVFile === null) {
          this.message = '输入文件不能为空！'
          this.showMessage = true
        } else {
          this.$refs.importCSVFileModal.hide()
          this.$refs.processingModal.show()
          let formData = new FormData()
          formData.append('file', this.uploadCSVFile, this.uploadCSVFile.name)
          formData.append('import_date', this.customDateSelection)
          this.importCSVFile(formData, this.customDateSelection)
        }
      } else {
        this.message = '日期格式有误！'
        this.showMessage = true
      }
    },
    onCancel (evt) {
      evt.preventDefault()
      this.$refs.importCSVFileModal.hide()
      this.setDefaultDate()
      this.uploadCSVFile = null
    },
    cleanAllInventoriesClose () {
      this.$refs.processingModal.hide()
      this.inventories = []
      this.inventoriesNum = 0
      this.inventoriesTotal = 0
      this.pageJump = 1
      this.pageCurr = 0
      this.pageTotal = 0
      this.pageOffset = 0
      this.pageOffsetMax = 0
      this.adminUsr = ''
      this.adminPwd = ''
    },
    cleanAllInventories (payload) {
      axios.post(this.serverBaseURL + '/api/v1/inventories/all/clean', payload)
        .then((res) => {
          if (res.data.status === 'success') {
            this.message = '删除成功！'
            this.showMessage = true
          } else if (res.data.status === 'invalid input data') {
            this.message = '删除失败，管理员账号或密码错误！'
            this.showMessage = true
          }
          this.cleanAllInventoriesClose()
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '导入失败!'
          this.showMessage = true
          this.cleanAllInventoriesClose()
        })
    },
    onCleanAllInventories (evt) {
      evt.preventDefault()
      this.$refs.CleanAllInventoriesModal.hide()
      this.$refs.processingModal.show()
      const payload = {
        admin_usr: this.adminUsr,
        admin_pwd: this.adminPwd
      }
      this.cleanAllInventories(payload)
    },
    onCancelCleanAllInventories (evt) {
      evt.preventDefault()
      this.$refs.CleanAllInventoriesModal.hide()
      this.adminUsr = ''
      this.adminPwd = ''
    },
    // ------------------------------ 销售报表（按分类汇总） ------------------------------
    fetchUI () {
      axios.get(this.serverBaseURL + '/api/v1/case1/ui/fetch')
        .then((res) => {
          this.customizeCase1.classification1_tags = res.data.ui.classification1_tags
          this.customizeCase1.classification1_classification2_tags = res.data.ui.classification1_classification2_tags
          this.customizeCase1.classification1_topk_tags = res.data.ui.classification1_topk_tags
          this.customizeCase1.brand_tags = res.data.ui.brand_tags
          this.customizeCase1.brand_topk_tag = res.data.ui.brand_topk_tag
          this.customizeCase1.brand_classification2_tags = res.data.ui.brand_classification2_tags
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '获取自定义UI失败！'
          this.showMessage = true
        })
    },
    saveUI (payload) {
      axios.post(this.serverBaseURL + '/api/v1/case1/ui/save', payload)
        .then(() => {
          this.message = '保存自定义UI成功！'
          this.showMessage = true
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '保存自定义UI失败！'
          this.showMessage = true
        })
    },
    onCustomizeCase1 (evt) {
      evt.preventDefault()
      this.$refs.customizeCase1Modal.show()
    },
    onSaveCustomizeCase1 (evt) {
      evt.preventDefault()
      const payload = {
        classification1_tags: this.customizeCase1.classification1_tags,
        classification1_classification2_tags: this.customizeCase1.classification1_classification2_tags,
        classification1_topk_tags: this.customizeCase1.classification1_topk_tags,
        brand_tags: this.customizeCase1.brand_tags,
        brand_topk_tag: this.customizeCase1.brand_topk_tag,
        brand_classification2_tags: this.customizeCase1.brand_classification2_tags
      }
      this.saveUI(payload)
      this.$refs.customizeCase1Modal.hide()
    },
    onCancelSaveCustomizeCase1 (evt) {
      evt.preventDefault()
      this.fetchUI()
      this.$refs.customizeCase1Modal.hide()
    },
    previewReportFileCase1Close () {
      this.$refs.processingModal.hide()
    },
    previewReportFileCase1 (payload) {
      axios.post(this.serverBaseURL + '/api/v1/case1/preview', payload)
        .then((res) => {
          if (res.data.status === 'success') {
            this.previewCase1.previewTable = Object.freeze(res.data.preview_table)
            this.$refs.previewCase1Modal.show()
          } else if (res.data.status === 'not found') {
            this.message = '预览失败！不存在指定的库存条目。'
            this.showMessage = true
          } else if (res.data.status === 'invalid tag') {
            this.message = res.data.err_msg
            this.showMessage = true
          }
          this.previewReportFileCase1Close()
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '预览失败！'
          this.showMessage = true
          this.previewReportFileCase1Close()
        })
    },
    onPreviewCase1 (evt) {
      evt.preventDefault()
      if ((this.stDateSelectionForCase1 === '') || (this.edDateSelection === '')) {
        this.message = '起始日期/截止日期不能为空！'
        this.showMessage = true
      } else if (this.dateReg.test(this.stDateSelectionForCase1) && this.dateReg.test(this.edDateSelection)) {
        this.$refs.processingModal.show()
        const payload = {
          st_date: this.stDateSelectionForCase1,
          ed_date: this.edDateSelection,
          ui_classification1_tags: this.customizeCase1.classification1_tags,
          ui_classification1_classification2_tags: this.customizeCase1.classification1_classification2_tags,
          ui_classification1_topk_tags: this.customizeCase1.classification1_topk_tags,
          ui_brand_tags: this.customizeCase1.brand_tags,
          ui_brand_topk_tag: this.customizeCase1.brand_topk_tag,
          ui_brand_classification2_tags: this.customizeCase1.brand_classification2_tags
        }
        this.previewReportFileCase1(payload)
      } else {
        this.message = '日期格式有误！'
        this.showMessage = true
      }
    },
    onCancelPreviewCase1 (evt) {
      evt.preventDefault()
      this.$refs.previewCase1Modal.hide()
    },
    onExportCase1 (evt) {
      evt.preventDefault()
      this.$refs.previewCase1Modal.hide()
      this.$refs.exportFileCase1Modal.hide()
      this.$refs.processingModal.show()
      const payload = {
        preview_table: this.previewCase1.previewTable
      }
      this.prepareExportReportFile('/api/v1/case1/prepare', payload)
    },
    onCancelExportCase1 (evt) {
      evt.preventDefault()
      this.$refs.exportFileCase1Modal.hide()
    },
    // ------------------------------ 销售报表（按系列汇总） ------------------------------
    previewReportFileCase2Close () {
      this.$refs.processingModal.hide()
    },
    previewReportFileCase2 (payload) {
      axios.post(this.serverBaseURL + '/api/v1/case2/preview', payload)
        .then((res) => {
          if (res.data.status === 'success') {
            this.previewCase2.previewTable = Object.freeze(res.data.preview_table)
            this.$refs.previewCase2Modal.show()
          } else if (res.data.status === 'not found') {
            this.message = '预览失败！不存在指定的库存条目。'
            this.showMessage = true
          }
          this.previewReportFileCase2Close()
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '预览失败！'
          this.showMessage = true
          this.previewReportFileCase2Close()
        })
    },
    onPreviewCase2 (evt) {
      evt.preventDefault()
      if ((this.stDateSelection === '') || (this.edDateSelection === '')) {
        this.message = '起始日期/截止日期不能为空！'
        this.showMessage = true
      } else if (this.dateReg.test(this.stDateSelection) && this.dateReg.test(this.edDateSelection)) {
        this.$refs.processingModal.show()
        const payload = {
          st_date: this.stDateSelection,
          ed_date: this.edDateSelection
        }
        this.previewReportFileCase2(payload)
      } else {
        this.message = '日期格式有误！'
        this.showMessage = true
      }
    },
    onCancelPreviewCase2 (evt) {
      evt.preventDefault()
      this.$refs.previewCase2Modal.hide()
    },
    onExportCase2 (evt) {
      evt.preventDefault()
      this.$refs.previewCase2Modal.hide()
      this.$refs.exportFileCase2Modal.hide()
      this.$refs.processingModal.show()
      const payload = {
        preview_table: this.previewCase2.previewTable
      }
      this.prepareExportReportFile('/api/v1/case2/prepare', payload)
    },
    onCancelExportCase2 (evt) {
      evt.preventDefault()
      this.$refs.exportFileCase2Modal.hide()
      // 恢复默认设置
      this.initExportForm()
    },
    // ------------------------------ 销售报表（按单个SKU汇总） ------------------------------
    previewReportFileCase3Close () {
      this.$refs.processingModal.hide()
    },
    previewReportFileCase3 (payload) {
      axios.post(this.serverBaseURL + '/api/v1/case3/preview', payload)
        .then((res) => {
          if (res.data.status === 'success') {
            this.previewCase3.previewTable = Object.freeze(res.data.preview_table)
            this.$refs.previewCase3Modal.show()
          } else if (res.data.status === 'not found') {
            this.message = '预览失败！不存在指定的库存条目。'
            this.showMessage = true
          }
          this.previewReportFileCase3Close()
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '预览失败！'
          this.showMessage = true
          this.previewReportFileCase3Close()
        })
    },
    onPreviewCase3 (evt) {
      evt.preventDefault()
      if ((this.stDateSelection === '') || (this.edDateSelection === '')) {
        this.message = '起始日期/截止日期不能为空！'
        this.showMessage = true
      } else if (this.dateReg.test(this.stDateSelection) && this.dateReg.test(this.edDateSelection)) {
        this.$refs.processingModal.show()
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
      } else {
        this.message = '日期格式有误！'
        this.showMessage = true
      }
    },
    onCancelPreviewCase3 (evt) {
      evt.preventDefault()
      this.$refs.previewCase3Modal.hide()
    },
    onExportCase3 (evt) {
      evt.preventDefault()
      this.$refs.previewCase3Modal.hide()
      this.$refs.exportFileCase3Modal.hide()
      this.$refs.processingModal.show()
      const payload = {
        preview_table: this.previewCase3.previewTable
      }
      this.prepareExportReportFile('/api/v1/case3/prepare', payload)
    },
    onCancelExportCase3 (evt) {
      evt.preventDefault()
      this.$refs.exportFileCase3Modal.hide()
      // 恢复默认设置
      this.initExportForm()
    },
    // ------------------------------ 滞销品报表 ------------------------------
    onExportCase4 (evt) {
      evt.preventDefault()
      this.$refs.previewCase4Modal.hide()
      this.$refs.exportFileCase4Modal.hide()
      this.$refs.processingModal.show()
      const payload = {
        preview_table: this.previewCase4.previewTable
      }
      this.prepareExportReportFile('/api/v1/case4/prepare', payload)
    },
    previewReportFileCase4Close () {
      this.$refs.processingModal.hide()
    },
    previewReportFileCase4 (payload) {
      axios.post(this.serverBaseURL + '/api/v1/case4/preview', payload)
        .then((res) => {
          if (res.data.status === 'success') {
            this.previewCase4.previewTable = Object.freeze(res.data.preview_table)
            this.$refs.previewCase4Modal.show()
          } else {
            this.message = '预览失败！不存在指定的库存条目。'
            this.showMessage = true
          }
          this.previewReportFileCase4Close()
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '预览失败！'
          this.showMessage = true
          this.previewReportFileCase4Close()
        })
    },
    onPreviewCase4 (evt) {
      evt.preventDefault()
      if ((this.stDateSelection === '') || (this.edDateSelection === '')) {
        this.message = '起始日期/截止日期不能为空！'
        this.showMessage = true
      } else if (this.dateReg.test(this.stDateSelection) && this.dateReg.test(this.edDateSelection)) {
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
        this.$refs.processingModal.show()
        this.previewReportFileCase4(payload)
      } else {
        this.message = '日期格式有误！'
        this.showMessage = true
      }
    },
    onCancelPreviewCase4 (evt) {
      evt.preventDefault()
      this.$refs.previewCase4Modal.hide()
    },
    onCancelExportCase4 (evt) {
      evt.preventDefault()
      this.$refs.exportFileCase4Modal.hide()
      // 恢复默认设置
      this.initExportForm()
    },
    // ------------------------------ 采购辅助分析报表 ------------------------------
    previewReportFileCase5WayClose () {
      this.$refs.processingModal.hide()
    },
    previewReportFileCase5Way (url, payload) {
      axios.post(this.serverBaseURL + url, payload)
        .then((res) => {
          if (res.data.status === 'success') {
            this.previewCase5.previewTable = Object.freeze(res.data.preview_table)
            this.supplierNameListFromScreeningWay1 = res.data.supplier_name_list_from_screening_way1
            this.$refs.previewCase5Modal.show()
          } else if (res.data.status === 'invalid operation') {
            this.message = '预览失败！请先操作筛选1！！！'
            this.showMessage = true
          } else {
            this.message = '预览失败！不存在指定的库存条目。'
            this.showMessage = true
          }
          this.previewReportFileCase5WayClose()
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '预览失败！'
          this.showMessage = true
          this.previewReportFileCase5WayClose()
        })
    },
    onPreviewCase5Pattern1 (evt) {
      evt.preventDefault()
      this.$refs.processingModal.show()
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
      this.$refs.processingModal.show()
      const payload = {
        supplier_name: this.supplierNameSelection,
        supplier_name_list_from_screening_way1: this.supplierNameListFromScreeningWay1,
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
    },
    onExportCase5 (evt) {
      evt.preventDefault()
      this.$refs.previewCase5Modal.hide()
      this.$refs.exportFileCase5Modal.hide()
      this.$refs.processingModal.show()
      const payload = {
        time_quantum_x: this.timeQuantumX,
        time_quantum_y: this.timeQuantumY,
        preview_table: this.previewCase5.previewTable
      }
      this.prepareExportReportFile('/api/v1/case5/prepare', payload)
    },
    onCancelExportCase5 (evt) {
      evt.preventDefault()
      this.$refs.exportFileCase5Modal.hide()
      // 恢复默认设置
      this.initExportForm()
    },
    // ------------------------------ 体积、重量计算汇总单 ------------------------------
    onImportForCase6 (evt) {
      evt.preventDefault()
      if (this.uploadCSVFileForCase6 === null) {
        this.message = '输入文件不能为空！'
        this.showMessage = true
      } else {
        this.$refs.processingModal.show()
        let formData = new FormData()
        formData.append('file', this.uploadCSVFileForCase6, this.uploadCSVFileForCase6.name)
        this.importCSVFileForCase6(formData)
      }
    },
    importCSVFileForCase6Close () {
      this.$refs.processingModal.hide()
    },
    importCSVFileForCase6 (formData) {
      let config = {
        header: {
          'Content-Type': 'multipart/form-data'
        }
      }
      axios.post(this.serverBaseURL + '/api/v1/case6/upload', formData, config)
        .then((res) => {
          if (res.data.status === 'success') {
            if (res.data.demand_table.length > 0) {
              this.message = '导入成功！'
              this.showMessage = true
              this.demandTable = res.data.demand_table
            } else {
              this.message = '导入成功！需求表是空的！'
              this.showMessage = true
            }
          } else if (res.data.status === 'invalid input data schema') {
            this.message = '导入失败！需求表格式有变更，请人工复核！'
            this.showMessage = true
          } else if (res.data.status === 'invalid input data') {
            this.message = '导入失败！' + res.data.err_msg
            this.showMessage = true
          }
          this.importCSVFileForCase6Close()
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '导入失败！'
          this.showMessage = true
          this.importCSVFileForCase6Close()
        })
    },
    onPreviewCase6 (evt) {
      evt.preventDefault()
      if (this.demandTable.length === 0) {
        this.message = '请先加载需求表！'
        this.showMessage = true
      } else {
        this.$refs.processingModal.show()
        const payload = {
          demand_table: this.demandTable
        }
        this.previewReportFileCase6(payload)
      }
    },
    previewReportFileCase6Close () {
      this.$refs.processingModal.hide()
    },
    previewReportFileCase6 (payload) {
      axios.post(this.serverBaseURL + '/api/v1/case6/preview', payload)
        .then((res) => {
          if (res.data.status === 'success') {
            this.previewCase6.previewTable = Object.freeze(res.data.preview_table)
            this.previewCase6.previewSummaryTable = res.data.preview_summary_table
            this.$refs.previewCase6Modal.show()
          } else {
            this.message = '预览失败！不存在指定的商品条目。'
            this.showMessage = true
          }
          this.previewReportFileCase6Close()
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '预览失败！'
          this.showMessage = true
          this.previewReportFileCase6Close()
        })
    },
    onExportCase6 (evt) {
      evt.preventDefault()
      this.$refs.previewCase6Modal.hide()
      this.$refs.exportFileCase6Modal.hide()
      this.$refs.processingModal.show()
      const payload = {
        preview_table: this.previewCase6.previewTable,
        preview_summary_table: this.previewCase6.previewSummaryTable
      }
      this.prepareExportReportFile('/api/v1/case6/prepare', payload)
    },
    onCancelPreviewCase6 (evt) {
      evt.preventDefault()
      this.$refs.previewCase6Modal.hide()
    },
    onCancelExportCase6 (evt) {
      evt.preventDefault()
      this.$refs.exportFileCase6Modal.hide()
      // 恢复默认设置
      this.initExportForm()
    },
    // ------------------------------ 文件统一下载 ------------------------------
    prepareExportReportFileClose () {
      this.$refs.processingModal.hide()
      // 恢复默认设置
      this.initExportForm()
    },
    prepareExportReportFile (url, payload) {
      axios.post(this.serverBaseURL + url, payload)
        .then((res) => {
          if (res.data.status === 'success') {
            this.exportReportFile(res.data.server_send_queue_file, res.data.output_file)
          } else if (res.data.status === 'not found') {
            this.message = '没有满足要求的数据条目！'
            this.showMessage = true
          }
          this.prepareExportReportFileClose()
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '下载失败！'
          this.showMessage = true
          this.prepareExportReportFileClose()
        })
    },
    exportReportFile (queryFile, saveFile) {
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
          this.message = '下载成功！保存为本地文件<' + saveFile + '>。'
          this.showMessage = true
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '下载失败！'
          this.showMessage = true
        })
    },
    // ------------------------------ 新增SKU下载 ------------------------------
    preDownloadAddedSKUs (payload) {
      axios.post(this.serverBaseURL + '/api/v1/addedskus/prepare', payload)
        .then((res) => {
          this.downloadAddedSKUs(res.data.server_send_queue_file, res.data.output_file)
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '下载失败！'
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
          this.message = '下载成功！保存为本地文件<' + saveFile + '>。'
          this.showMessage = true
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.log(error)
          this.message = '下载失败！'
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
    // ------------------------------ 翻页 ------------------------------
    onFirstPage (evt) {
      evt.preventDefault()
      this.pageOffset = 0
      this.listInventories()
    },
    onJumpPage (evt) {
      evt.preventDefault()
      if (this.pageJump <= 0 || this.pageJump > this.pageTotal) {
        this.pageOffset = 0
      } else {
        this.pageOffset = (this.pageJump - 1) * 20
      }
      this.listInventories()
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
    onLastPage (evt) {
      evt.preventDefault()
      this.pageOffset = this.pageOffsetMax
      this.listInventories()
    },
    // ------------------------------ 设置默认日期值 ------------------------------
    setDefaultDate () {
      var today = new Date()
      var year = today.getFullYear() * 1
      var month = today.getMonth() * 1
      // 为导入时间设置默认值
      if (month >= 10) {
        this.customDateSelection = year.toString() + '-' + month.toString()
      } else if (month < 10 && month >= 2) {
        this.customDateSelection = year.toString() + '-0' + month.toString()
      } else {
        this.customDateSelection = (year - 1).toString() + '-12'
      }
      // 为起始时间设置默认值
      this.stDateSelectionForCase1 = this.customDateSelection
      var stYear
      var stMonth
      if (month - 2 < 0) {
        stYear = year - 1
        stMonth = month - 2 + 12
      } else {
        stYear = year
        stMonth = month - 2
      }
      if (stMonth >= 10) {
        this.stDateSelection = stYear.toString() + '-' + stMonth.toString()
      } else if (stMonth < 10 && stMonth >= 2) {
        this.stDateSelection = stYear.toString() + '-0' + stMonth.toString()
      } else {
        this.stDateSelection = (stYear - 1).toString() + '-12'
      }
      // 为截止时间设置默认值
      this.edDateSelection = this.customDateSelection
    }
  },
  created () {
    console.log(process.env.NODE_ENV)
    console.log(process.env.SERVER_BASE_URL)
    this.listAllOptions()
    this.listAllSupplierSelections()
    this.listInventories()
    this.getInventoriesTotal()
    this.setDefaultDate()
    this.fetchUI()
  }
}
</script>
