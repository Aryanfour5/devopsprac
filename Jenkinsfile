pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'node:18-alpine'
        PY_IMAGE = 'python:3.11-slim'
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
                sh '''
                    docker build -t calculator-app:${BUILD_NUMBER} .
                '''
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
                    sleep 3
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo "✅ Health checking..."
                sh '''
                    for i in {1..10}; do
                        if curl -f http://localhost:3000/health; then
                            echo "App is healthy!"
                            exit 0
                        fi
                        sleep 1
                    done
                    exit 1
                '''
            }
        }

        stage('Run Pytest') {
            steps {
                echo "🧪 Running pytest..."
                sh '''
                    docker run --rm \
                      -e APP_URL=http://host.docker.internal:3000 \
                      -v ${WORKSPACE}:/workspace \
                      -w /workspace \
                      ${PY_IMAGE} \
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
        }
        success {
            echo "🎉 Build successful!"
            junit 'test-results.xml'
        }
        failure {
            echo "❌ Build failed!"
        }
    }
}
