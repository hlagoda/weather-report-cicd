pipeline{
    agent any
    
    options {
        ansiColor('xterm')
    }

    stages {
        stage('Install 3rd party components'){
            steps{
                sh 'ansible-playbook app_execute.yml -t install_components -i {{ playbook_dir }}/workspace/inventory.yml --vault-password-file vault_pass.txt'
            }
        }
        stage('Add files to {{ project.name}}-agent vm'){
            steps{
                sh 'ansible-playbook app_execute.yml -t add_files -i {{ playbook_dir }}/workspace/inventory.yml --vault-password-file vault_pass.txt'
            }
        }
        stage('Deploy docker containers'){
            steps{
                sh 'ansible-playbook app_execute.yml -t deploy_docker -i {{ playbook_dir }}/workspace/inventory.yml --vault-password-file vault_pass.txt'
            }
        }
        stage('Run Docker containers') {
            steps {
                sh 'docker-compose up -d'
            }
        }
    }
}