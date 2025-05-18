pipeline{
    agent any

    options {
        ansiColor('xterm')
    }

    stages {
        stage('Fetch the data') {
            steps {
                sh 'docker-compose run --rm fetch_app'
            }
        }
        stage('Create report') {
            steps {
                sh 'docker-compose run --rm report_app'
            }
        }
        stage('Send report to S3') {
            steps {
                sh 'docker-compose run --rm send_report'
            }
        }
    }

    triggers {
        cron('H * * * *') 
    }
}