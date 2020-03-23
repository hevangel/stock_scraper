pipeline {
    agent any
    environment {
        ENV_VAR1 = 'Horace'
        ENV_VAR2 = 'Chan'
    }
    stages {
        stage('build') {
            steps {
                sh 'echo $ENV_VAR1 $ENV_VAR2'
                sh 'python --version'
            }
        }
        stage('test') {
            steps {
                sh 'echo "hello world"'
            }
            steps {
                sh 'python3 test.py'
            }
        }
        stage('deploy') {
            steps {
                input 'Does the stage ok?'
            }
        }
    }
    post {
        always {
            echo 'This will always run'
            archiveArtifacts artifacts: 'data_finviz/*', fingerprint: true
            juint 'output.xml'
            mail to : 'hevangel@yahoo.com'
                subject: 'failed pipeline: ${currentBuild.fullDisplayName}'
                body: 'something is wrong with ${env.BUILD_URL}'
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
