pipeline {
    agent any
    environment {
        ENV_VAR1 = 'Horace'
        ENV_VAR2 = 'Chan'
    }
    stages {
        stage('build') {
            steps {
                sh 'echo $BUILD_TIMESTAMP'
                // sh 'python3 scrap_finviz_screener.py'
            }
        }
        stage('test') {
            steps {
                sh 'echo "hello world"'
                sh 'python3 test.py'
            }
        }
        //stage('deploy') {
        //    steps {
        //        input 'Does the stage ok?'
        //    }
        //}
    }
    post {
        always {
            echo 'This will always run'
            archiveArtifacts artifacts: 'data_finviz/finviz_${BUILD_TIMESTAMP}.csv', fingerprint: true
            junit 'output.xml'
        }
        success {
            echo 'This will run only if successful'
        }
        failure {
            echo 'This will run only if failed'
        }
        unstable {
            echo 'This will run only if the run was marked as unstable'
        }
        changed {
            echo 'This will run only if the state of the Pipeline has changed'
            echo 'For example, if the Pipeline was previously failing but is now successful'
        }
    }
}
