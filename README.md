# devops

    python 3.6 + django 1.11 
    
    requirements: pymysql zabbix_client

https://www.cnblogs.com/zny/p/10072938.html pymysql


# vue
    官网下载nodejs 安装
    cnpm 安装 : npm install -g cnpm --registry=https://registry.npm.taobao.org
    安装webpack : cnpm install webpack -g
    安装vuecli : cnpm install -g @vue/cli
    创建一个项目: vue create vue-project                  https://www.cnblogs.com/liuqiuyue/p/9699796.html
    安装vue-route : cnpm install vue-router -S
    安装element : npm i element-ui -S
    安装 vue-fontawesome : https://github.com/FortAwesome/vue-fontawesome#installation  https://www.hangge.com/blog/cache/detail_2104.html
        cnpm install --save @fortawesome/fontawesome-svg-core @fortawesome/free-regular-svg-icons @fortawesome/free-solid-svg-icons @fortawesome/vue-fontawesome @fortawesome/free-brands-svg-icons
    配置 vue-fontawesome :
        import { library } from '@fortawesome/fontawesome-svg-core'
        import { fas } from '@fortawesome/free-solid-svg-icons'
        import { fab } from '@fortawesome/free-brands-svg-icons'
        import { far } from '@fortawesome/free-regular-svg-icons'
        import { FontAwesomeIcon, FontAwesomeLayers, FontAwesomeLayersText } from '@fortawesome/vue-fontawesome'
        library.add(fas, far, fab)
        Vue.component('font-awesome-icon', FontAwesomeIcon)
        Vue.component('font-awesome-layers', FontAwesomeLayers)
        Vue.component('font-awesome-layers-text', FontAwesomeLayersText)
    
    启动:  cd vue-project  cnpm run serve

