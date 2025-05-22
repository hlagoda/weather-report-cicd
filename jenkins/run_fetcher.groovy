pipeline{
    agent any

    options {
        ansiColor('xterm')
    }

    stages {
        stage('Fetch the data') {
            steps {
                sh 'docker-compose run fetch_app'
            }
        }
        stage('Create report') {
            steps {
                sh 'docker-compose run report_app'
            }
        }
        stage('Send report to S3') {
            steps {
                sh 'docker-compose run send_report'
            }
        }
    }

    triggers {
        cron('H * * * *') 
    }
}