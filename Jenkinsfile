pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "calculator-app:${BUILD_NUMBER}"
        DOCKER_IMAGE_LATEST = "calculator-app:latest"
        APP_CONTAINER = "calculator-app-${BUILD_NUMBER}"
        TEST_RESULTS = "test-results.xml"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "Repository checked out successfully"
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image: ${DOCKER_IMAGE}"
                    sh 'docker build -t ${DOCKER_IMAGE} -t ${DOCKER_IMAGE_LATEST} .'
                    sh 'docker images | grep calculator-app'
                }
            }
        }

        stage('Start Application') {
            steps {
                script {
                    echo "Starting calculator application container"
                    sh '''
                        docker run -d \
                            --name ${APP_CONTAINER} \
                            -p 3000:3000 \
                            ${DOCKER_IMAGE}
                        
                        sleep 3
                        docker ps | grep ${APP_CONTAINER}
                    '''
                }
            }
        }

        stage('Run Pytest') {
            steps {
                script {
                    echo "Running pytest tests"
                    sh '''
                        docker run --rm \
                            --network host \
                            -e APP_URL=http://localhost:3000 \
                            -v ${WORKSPACE}:/workspace \
                            ${DOCKER_IMAGE} \
                            python3 -m pytest /workspace/tests/test_calculator.py \
                            --junitxml=/workspace/${TEST_RESULTS} \
                            --tb=short \
                            -v
                    '''
                }
            }
        }

        stage('Generate Coverage Report') {
            steps {
                script {
                    echo "Generating coverage report"
                    sh '''
                        docker run --rm \
                            --network host \
                            -e APP_URL=http://localhost:3000 \
                            -v ${WORKSPACE}:/workspace \
                            ${DOCKER_IMAGE} \
                            python3 -m pytest /workspace/tests/test_calculator.py \
                            --cov=. \
                            --cov-report=html:/workspace/coverage-report \
                            --tb=short || true
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                echo "Cleaning up containers"
                sh 'docker stop ${APP_CONTAINER} || true'
                sh 'docker rm ${APP_CONTAINER} || true'
            }
        }

        success {
            echo "Pipeline executed successfully"
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'coverage-report',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])
        }

        failure {
            echo "Pipeline failed"
            archiveArtifacts artifacts: '${TEST_RESULTS}', allowEmptyArchive: true
        }
    }
}

// Publish test results to Jenkins
junit testResults: '${TEST_RESULTS}', allowEmptyResults: false
