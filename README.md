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
# python3 venv
    pip3 install virtualenv
    mkdir projects
    cd projects
    virtualenv --no-site-packages venv
    source venv/bin/activate
    pip3 freeze > requirements.txt 
    pip3 install -r requirements.txt
    
# github 一个仓库放多个项目
    1. 创建好仓库 https://github.com/linchqd/DockerUI.git
    2. git clone 到本地
    3. git checkout --orphan 分支名称(api)   创建分支api并进入api分支, 然后把里边的内容清空, 创建api分支的内容文件
    4. 然后git add / git commit /  git branch --set-upstream-to=origin/api api  /  git pull origin/master api  即可
    5. 拉取分支代码: git clone -b api https://github.com/linchqd/DockerUI.git ~/api  即可将分支api克隆到家目录的api目录下
    
# https://github.com/CentOS/CentOS-Dockerfiles


