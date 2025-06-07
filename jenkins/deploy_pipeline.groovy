def deploy() {
    node('master') {
        stage('Install 3rd party components') {
            dir('/opt/weather-report-cicd') {
                sh '''
                    ansible-playbook app_execute.yml \
                      -t install_components \
                      --vault-password-file vault_pass.txt \
                      --ssh-common-args="-o StrictHostKeyChecking=no"
                '''
            }
        }

        stage('Add files to agent') {
            dir('/opt/weather-report-cicd') {
                sh '''
                    ansible-playbook app_execute.yml \
                      -t add_files \
                      --vault-password-file vault_pass.txt \
                      --ssh-common-args="-o StrictHostKeyChecking=no"
                '''
            }
        }

        stage('Deploy docker containers') {
            dir('/opt/weather-report-cicd') {
                sh '''
                    ansible-playbook app_execute.yml \
                      -t deploy_docker \
                      --vault-password-file vault_pass.txt \
                      --ssh-common-args="-o StrictHostKeyChecking=no"
                '''
            }
        }

        stage('Run Docker containers') {
            dir('/opt/weather-report-cicd') {
                sh '''
                    ansible-playbook app_execute.yml \
                      -t run_docker \
                      --vault-password-file vault_pass.txt \
                      --ssh-common-args="-o StrictHostKeyChecking=no"
                '''
            }
        }
    }
}

return this
