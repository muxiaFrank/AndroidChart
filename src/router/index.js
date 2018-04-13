import Vue from 'vue'
import Router from 'vue-router'
import Android from '@/components/Android'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Android',
      component: Android
    }
  ]
})
