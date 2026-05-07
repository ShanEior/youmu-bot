import { createRouter, createWebHistory } from 'vue-router'
import UploadView from '../views/UploadView.vue'
import PreviewView from '../views/PreviewView.vue'
import ResultView from '../views/ResultView.vue'

const routes = [
  {
    path: '/',
    redirect: '/upload',
  },
  {
    path: '/upload',
    name: 'upload',
    component: UploadView,
  },
  {
    path: '/preview',
    name: 'preview',
    component: PreviewView,
  },
  {
    path: '/result',
    name: 'result',
    component: ResultView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
