pipeline{
    agent any
    
    options {
        ansiColor('xterm')
    }

    stages {
        stage('Build & Deploy') {
            steps {
                sh 'docker-compose up -d'
            }
        }
    }
}