#!/usr/bin/groovy
pipeline {
    agent { docker { image 'psamsotha/scrumptious-python-testing' } }
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/psamsotha-ss/ss-driver-location-streaming.git', branch: 'cicd-jenkins'
            }
        }
//         stage('SonarQube Analysis') {
//             environment {
//                 SONARQUBE_TOKEN = credentials('sonarqube-token')
//             }
//             steps {
//                 sh "./mvnw sonar:sonar \\\n" +
//                         "  -Dsonar.projectKey=jersey-api \\\n" +
//                         "  -Dsonar.host.url=http://sonarqube:9000 \\\n" +
//                         "  -Dsonar.login=${SONARQUBE_TOKEN}"
//             }
//         }
//         stage('InstallDependencies') {
//             steps {
//                 sh 'pip install -r requirements.txt'
//             }
//         }
        stage('Test') {
            steps {
                sh './runtests.sh'
            }
        }
//         stage('Build') {
//             steps {
//                 sh './mvnw package -DskipTests'
//             }
//             post {
//                 success {
//                     archiveArtifacts artifacts: 'target/*jar'
//                 }
//             }
//         }
//         stage('S3 Archive Upload') {
//             steps {
//                 withAWS(region: 'us-west-2', credentials: 'SmoothstackAws') {
//                     s3Upload(bucket: 'psamsotha-smoothstack', file: 'target/smoothstack-ec2-jersey-api.jar',
//                             path: 'devops-training/smoothstack-ec2-jersey-api.jar')
//                 }
//             }
//         }
//         stage('Pull Archive') {
//             steps {
//                 withAWS(region: 'us-west-2', credentials: 'SmoothstackAws') {
//                     s3Download(bucket: 'psamsotha-smoothstack', file: '/var/jenkins_home/app/smoothstack-ec2-jersey-api.jar',
//                             path: 'devops-training/smoothstack-ec2-jersey-api.jar', force: true)
//                 }
//             }
//         }
//         stage('Deploy') {
//             steps {
//                 // envar required for spawning background process
//                 withEnv(['JENKINS_NODE_COOKIE=dontKillMe']) {
//                     sh 'nohup java -jar /var/jenkins_home/app/smoothstack-ec2-jersey-api.jar &'
//                 }
//             }
//         }
    }
}