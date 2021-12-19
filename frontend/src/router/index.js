import Vue from 'vue'
import VueRouter from 'vue-router'

import Inventory from '@/components/Inventory'
import OpLog from '@/components/OpLog'
import Product from '@/components/Product'
import SelectionList from '@/components/SelectionList'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Inventory',
    component: Inventory
  },
  {
    path: '/oplog',
    name: 'OpLog',
    component: OpLog
  },
  {
    path: '/product',
    name: 'Product',
    component: Product
  },
  {
    path: '/slist',
    name: 'SelectionList',
    component: SelectionList
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
