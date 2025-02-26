import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
// import components from '@/components/ui'







// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'; 
import DayJsAdapter from '@date-io/dayjs'



const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',


  },
  date: {
    adapter: DayJsAdapter,
  },
  
})

const app = createApp(App)

// components.forEach(component => {
//     app.component(component.name, component)
// });


app.use(store).use(vuetify).use(router).mount('#app')
