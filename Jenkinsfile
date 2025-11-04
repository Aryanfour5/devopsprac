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
                checkout(scm)
                sh '''
                    echo "Repository contents:"
                    ls -la
                    echo "\nTests directory:"
                    ls -la tests/
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh '''
                    echo "Installing dependencies..."
                    node --version
                    npm install
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "Building Docker image: ${DOCKER_IMAGE}"
                    docker build -t ${DOCKER_IMAGE} -t ${DOCKER_IMAGE_LATEST} .
                    docker images | grep calculator-app
                '''
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
                        docker logs ${APP_CONTAINER} || true
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
                    docker logs ${APP_CONTAINER} || true
                    exit 1
                '''
            }
        }
        
        stage('Run Pytest') {
    steps {
        sh '''
            echo "Installing test requirements..."
            pip3 install -q pytest requests pytest-cov
            
            echo "Running pytest against running app on localhost:3000..."
            python3 -m pytest tests/test_calculator.py \\
                -v \\
                --tb=short \\
                --junitxml=test-results.xml \\
                -e APP_URL=http://localhost:3000
        '''
    }
}



        
        stage('Generate Coverage Report') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                sh '''
                    echo "Generating coverage report..."
                    docker run --rm \
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
    
    post {
        always {
            sh '''
                echo "Cleaning up containers..."
                docker stop ${APP_CONTAINER} 2>/dev/null || echo "Container already stopped"
                docker rm ${APP_CONTAINER} 2>/dev/null || echo "Container already removed"
            '''
        }
        
        success {
            script {
                if (fileExists('${TEST_RESULTS}')) {
                    junit testResults: '${TEST_RESULTS}', allowEmptyResults: false
                }
            }
            
            script {
                if (fileExists('coverage-report/index.html')) {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'coverage-report',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
            
            echo "✓ Build and tests successful!"
        }
        
        failure {
            script {
                if (fileExists('${TEST_RESULTS}')) {
                    junit testResults: '${TEST_RESULTS}', allowEmptyResults: true
                    archiveArtifacts artifacts: '${TEST_RESULTS}', allowEmptyArchive: true
                }
            }
            
            sh '''
                echo "=== Build Failed ==="
                echo "Last container logs:"
                docker logs ${APP_CONTAINER} 2>/dev/null || echo "No logs available"
                
                echo "\nWorkspace contents:"
                ls -la ${WORKSPACE}
                
                echo "\nTest files:"
                find ${WORKSPACE} -name "*.py" -type f 2>/dev/null || echo "No Python files found"
            '''
        }
    }
}



