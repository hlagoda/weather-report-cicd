pipeline{
    agent any
    
    options {
        ansiColor('xterm')
    }

    stages {
        stage('Install components') {
            steps {
                sh 'ansible-playbook -i inventory.yml app_execute.yml -t install_components'
            }
        }
        stage('Deploy Docker containers') {
            steps {
                sh 'ansible-playbook -i inventory.yml app_execute.yml -t deploy_docker'
            }
        }
    }
}