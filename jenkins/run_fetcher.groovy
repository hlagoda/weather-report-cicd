def deploy() {
    node('master') {
        stage('Fetch the data') {
            dir('/opt/weather-report-cicd'){
                sh '''
                    ansible-playbook app_execute.yml \
                      -t run_docker \
                      --vault-password-file vault_pass.txt \
                      --ssh-common-args="-o StrictHostKeyChecking=no" \
                      -e "to_run=fetch_app"
                    '''
                }
            }
        stage('Send report to S3') {
            dir('/opt/weather-report-cicd'){
                sh '''
                ansible-playbook app_execute.yml \
                  -t run_docker \
                  --vault-password-file vault_pass.txt \
                  --ssh-common-args="-o StrictHostKeyChecking=no" \
                  -e "to_run=send_report"
                '''
            }
        }
    }
}

return this
