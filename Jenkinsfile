pipeline {
    agent any

    environment {
        APP_CONTAINER = "calculator-app-${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t calculator-app:${BUILD_NUMBER} .'
            }
        }

        stage('Start Application') {
            steps {
                sh '''
                    docker run -d \
                      --name ${APP_CONTAINER} \
                      -p 3000:3000 \
                      calculator-app:${BUILD_NUMBER}
                    sleep 10
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    for i in {1..30}; do
                        if docker logs ${APP_CONTAINER} | grep -qi "running on port 3000"; then
                            echo "✓ App is running!"
                            exit 0
                        fi
                        echo "Waiting... ($i/30)"
                        sleep 1
                    done
                    echo "✗ App failed to start"
                    exit 1
                '''
            }
        }

stage('Run Tests') {
    steps {
        sh '''
            # Run tests using docker run with proper volume mounting
            docker run --rm --network host \
                -v "$(pwd)":/workspace \
                -w /workspace \
                python:3.11-slim /bin/sh -c \
                "pip install -q pytest requests && python3 -m pytest tests/ -v --tb=short --junitxml=test-results.xml"
        '''
    }
}
    steps {
        sh '''
            pip install -q pytest requests
            python3 -m pytest tests/ -v --tb=short --junitxml=test-results.xml
        '''
    }
}
    }

    post {
        always {
            sh 'docker stop ${APP_CONTAINER} 2>/dev/null || true'
            sh 'docker rm ${APP_CONTAINER} 2>/dev/null || true'
            junit 'test-results.xml'
        }
        success {
            echo "✅ Build successful!"
        }
        failure {
            echo "❌ Build failed!"
        }
    }
}





