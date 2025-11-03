pipeline {
    agent {
        docker { image 'node:18-alpine' }
    }
    
    environment {
        DOCKER_IMAGE = "calculator-app:${BUILD_NUMBER}"
        DOCKER_IMAGE_LATEST = "calculator-app:latest"
        APP_CONTAINER = "calculator-app-${BUILD_NUMBER}"
        TEST_RESULTS = "test-results.xml"
    }
    
    stages {
        stage('Install Dependencies') {
            steps {
                sh 'node --version'
                sh 'npm install'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${DOCKER_IMAGE} -t ${DOCKER_IMAGE_LATEST} .'
                sh 'docker images | grep calculator-app'
            }
        }
        
        stage('Start Application') {
            steps {
                sh '''
                    docker run -d \
                        --name ${APP_CONTAINER} \
                        -p 3000:3000 \
                        ${DOCKER_IMAGE}
                    
                    sleep 5
                    docker ps | grep ${APP_CONTAINER}
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                sh '''
                    for i in {1..30}; do
                        if curl -f http://localhost:3000/health; then
                            echo "App is healthy"
                            exit 0
                        fi
                        echo "Attempt $i: App not ready, waiting..."
                        sleep 2
                    done
                    echo "App failed health check"
                    exit 1
                '''
            }
        }
        
        stage('Run Pytest') {
            steps {
                sh '''
                    pip install pytest pytest-cov requests
                    python3 -m pytest tests/test_calculator.py \
                        --junitxml=${TEST_RESULTS} \
                        --tb=short \
                        -v
                '''
            }
        }
        
        stage('Generate Coverage Report') {
            steps {
                sh '''
                    python3 -m pytest tests/test_calculator.py \
                        --cov=. \
                        --cov-report=html:coverage-report \
                        --tb=short || true
                '''
            }
        }
    }
    
    post {
        always {
            sh 'docker stop ${APP_CONTAINER} || true'
            sh 'docker rm ${APP_CONTAINER} || true'
        }
        
        success {
            junit testResults: '${TEST_RESULTS}', allowEmptyResults: false
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
            junit testResults: '${TEST_RESULTS}', allowEmptyResults: true
            archiveArtifacts artifacts: '${TEST_RESULTS}', allowEmptyArchive: true
        }
    }
}
