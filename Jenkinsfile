pipeline {
    agent any

    environment {
        APP_CONTAINER = "calculator-app-${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "📦 Checking out code..."
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "🔨 Building Docker image..."
                sh 'docker build -t calculator-app:${BUILD_NUMBER} .'
            }
        }

        stage('Start Application') {
            steps {
                echo "🚀 Starting application..."
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
                echo "✅ Health checking..."
                sh '''
                    for i in {1..30}; do
                        echo "Attempt $i/30..."
                        if docker logs ${APP_CONTAINER} | grep -q "listening on port 3000"; then
                            echo "✓ App started!"
                            exit 0
                        fi
                        sleep 1
                    done
                    echo "✗ App failed to start"
                    docker logs ${APP_CONTAINER}
                    exit 1
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo "🧪 Running pytest..."
                sh '''
                    docker run --rm \
                      -e APP_URL=http://172.17.0.1:3000 \
                      -v ${WORKSPACE}:/workspace \
                      -w /workspace \
                      python:3.11-slim \
                      /bin/sh -c "pip install -q pytest requests && python3 -m pytest tests/ -v --tb=short --junitxml=test-results.xml"
                '''
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up..."
            sh '''
                docker stop ${APP_CONTAINER} 2>/dev/null || true
                docker rm ${APP_CONTAINER} 2>/dev/null || true
            '''
            junit 'test-results.xml'
        }
        success {
            echo "🎉 All tests passed!"
        }
        failure {
            echo "❌ Build failed!"
            sh 'docker logs ${APP_CONTAINER} || true'
        }
    }
}
