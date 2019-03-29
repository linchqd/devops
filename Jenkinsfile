pipeline {
    agent {
        label 'jnlp-slave-java'
    }
    options {
        //仅保留最近 10 次的构建记录
        buildDiscarder(logRotator(numToKeepStr: '10'))
        //输出时间戳
        timestamps()
    }
    environment {
        //定义 build 的源码分支
        BRANCH_NAME = 'master'
        //定义应用名称
        APP_NAME = 'devops'
        //定义 Docker Registry 认证信息
        DOCKERREG_ACCESS_KEY = credentials('harbor-access-key')
        //定义 Docker Registry 地址
        DOCKERREG_DOMAIN = '192.168.0.11'
        //定义镜像所归属的 Namespace
        TARGET_NAMESPACE = 'library'
        //定义镜像的 Tag(即版本号由 VersionNumber 插件动态生成)
        //格式：<用于 build 的源码分支>-<build 的所属年月日>-<当天的第 N 次build>
        IMAGE_TAG = VersionNumber(projectStartDate: '1970-01-01',versionNumberString: '${BUILD_DATE_FORMATTED, "yyyyMMdd"}-${BUILDS_TODAY,XXX}', versionPrefix: "${BRANCH_NAME}-")
        //应用镜像的完整构成
        APP_DOCKER_IMAGE="${DOCKERREG_DOMAIN}/${TARGET_NAMESPACE}/${APP_NAME}:${IMAGE_TAG}"
    }
    stages {
        //stage('checkout code') {
        //    steps {
                //gitlab拉取代码
        //        git credentialsId: 'gitlab-access-key', url: 'http://gitlab.default/dev/devops.git'
        //    }
        //}
        //stage('Build project package') {
        //    steps {
                //利用 maven 对项目进行 build
        //        sh 'mvn clean package -Dmaven.test.skip'
                //检查应用的包
        //        sh 'ls -l target | grep war'
        //    }
        //}
        stage('Build Docker Image') {
            steps {
                //以项目根目录为构建上下文 根据 Dockerfile 构建应用镜像
                sh "docker build -t ${APP_DOCKER_IMAGE} ."
            }
        }
        stage('Push Docker Image') {
            steps {
                //先登录Docker Registry
                sh "docker login -u ${DOCKERREG_ACCESS_KEY_USR} -p ${DOCKERREG_ACCESS_KEY_PSW} https://${DOCKERREG_DOMAIN}"
                //将所构建的镜像推送到Docker Registry
                sh "docker push ${APP_DOCKER_IMAGE}"
            }
        }
        stage('Update Application') {
            steps {
                //先通过 sed 命令devops.yaml 中的 IMAGE_TAG 替换为实际的版本号
                sh "sed -i 's/IMAGE_TAG/${IMAGE_TAG}/g' devops.yaml"
                //然后调用 kubectl apply 命令去更新应用
                sh 'kubectl apply -f devops.yaml --record'
            }
        }
    }
}
