<template>
  <div class="row">
    <div class="col-sm-12">
      <b-navbar type="dark" variant="dark">
        <b-navbar-nav>
        <b-nav-item :active="false" href="/product">商品明细库</b-nav-item>
        <b-nav-item :active="true" href="/">库存明细库</b-nav-item>
        <b-nav-item :active="false" href="/slist">辅助查询</b-nav-item>
        <b-nav-item :active="false" href="/oplog">操作日志</b-nav-item>
        <b-nav-item :active="false" href="/user" v-if="showUserManagementModule">用户管理</b-nav-item>
        </b-navbar-nav>
      </b-navbar>
  </div>
</div>
</template>

<script>
export default {
  created () {
    if (this.$cookies.isKey('role')) {
      if (this.$cookies.get('role') === 'role=0') {
        this.showUserManagementModule = true
      } else {
        this.showUserManagementModule = false
      }
    } else {
      this.showUserManagementModule = false
    }
  }
}
</script>
