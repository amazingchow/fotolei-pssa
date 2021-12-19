<template>
  <div id="app">
    <div>
      <b-navbar type="dark" variant="success">
        <b-navbar-nav>
          <b-nav-item href="/product">商品明细库</b-nav-item>
          <b-nav-item href="/">库存明细库</b-nav-item>
          <b-nav-item href="/slist">搜索项列表</b-nav-item>
          <b-nav-item href="/oplog">操作日志</b-nav-item>
        </b-navbar-nav>
      </b-navbar>
    </div>
    <br>
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  margin-top: 0px;
  margin-bottom: 0px;
  margin-left: 20px;
  margin-right: 20px;
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: left;
  color: #2c3e50;
}
</style>
