pipeline {
    agent any
    
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
                    echo "Starting calculator app container..."
                    docker run -d \
                        --name ${APP_CONTAINER} \
                        -p 3000:3000 \
                        ${DOCKER_IMAGE}
                    
                    echo "Waiting 5 seconds for startup..."
                    sleep 5
                    
                    echo "Checking if container is running..."
                    if docker ps | grep ${APP_CONTAINER}; then
                        echo "✓ Container is running"
                    else
                        echo "✗ Container failed to start!"
                        echo "Container logs:"
                        docker logs ${APP_CONTAINER}
                        exit 1
                    fi
                '''
            }
        }
        
        stage('Health Check') {
    steps {
        sh '''
            echo "Running health check..."
            for i in {1..30}; do
                echo "Attempt $i/30: Checking health endpoint..."
                if docker exec ${APP_CONTAINER} node -e "
                    const http = require('http');
                    http.get('http://localhost:3000/health', (res) => {
                        process.exit(res.statusCode === 200 ? 0 : 1);
                    }).on('error', () => process.exit(1));
                    setTimeout(() => process.exit(1), 5000);
                " 2>/dev/null; then
                    echo "✓ App is healthy!"
                    exit 0
                fi
                sleep 2
            done
            
            echo "✗ App failed health check"
            docker logs ${APP_CONTAINER}
            exit 1
        '''
    }
}


        
        stage('Run Pytest') {
            steps {
                sh '''
                    echo "Installing test dependencies..."
                    pip3 install --break-system-packages pytest pytest-cov requests
                    
                    echo "Running tests..."
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
                    echo "Generating coverage report..."
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
            sh '''
                echo "Cleaning up..."
                docker stop ${APP_CONTAINER} 2>/dev/null || echo "Container already stopped"
                docker rm ${APP_CONTAINER} 2>/dev/null || echo "Container already removed"
            '''
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
            
            echo "✓ Build successful!"
        }
        
        failure {
            junit testResults: '${TEST_RESULTS}', allowEmptyResults: true
            archiveArtifacts artifacts: '${TEST_RESULTS}', allowEmptyArchive: true
            
            sh '''
                echo "=== Build Failed ==="
                echo "Last container logs:"
                docker logs ${APP_CONTAINER} 2>/dev/null || echo "No logs available"
            '''
        }
    }
}


