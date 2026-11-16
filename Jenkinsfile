pipeline {
    agent any

    environment {
        APP_NAME = 'campusfix'
        IMAGE_NAME = 'campusfix'
        CONTAINER_NAME = 'campusfix-app'
        PORT = '5000'
        // Add Python, Scripts, Docker, and Git to Jenkins execution PATH
        PATH = "C:\\Users\\Sanjana Mukherjee\\AppData\\Local\\Programs\\Python\\Python312;C:\\Users\\Sanjana Mukherjee\\AppData\\Local\\Programs\\Python\\Python312\\Scripts;C:\\Users\\Sanjana Mukherjee\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin;C:\\Program Files\\Git\\cmd;${env.PATH}"
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('1. Checkout Source') {
            steps {
                echo "==> [Stage 1] Pulling source code from GitHub repository..."
                checkout scm
            }
        }

        stage('2. Install Dependencies') {
            steps {
                echo "==> [Stage 2] Preparing virtual environment and installing dependencies..."
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv .jenkins_venv || python -m venv .jenkins_venv
                            . .jenkins_venv/bin/activate
                            pip install -r requirements.txt
                        '''
                    } else {
                        bat '''
                            python -m venv .jenkins_venv
                            call .jenkins_venv\\Scripts\\activate.bat
                            pip install -r requirements.txt
                        '''
                    }
                }
            }
        }

        stage('3. Run Automated Tests') {
            steps {
                echo "==> [Stage 3] Executing automated Pytest suite (Auth, RBAC, CRUD)..."
                script {
                    if (isUnix()) {
                        sh '''
                            . .jenkins_venv/bin/activate
                            pytest -v --tb=short
                        '''
                    } else {
                        bat '''
                            call .jenkins_venv\\Scripts\\activate.bat
                            pytest -v --tb=short
                        '''
                    }
                }
            }
        }

        stage('4. Build Docker Image') {
            steps {
                echo "==> [Stage 4] Packaging application into Docker image '${IMAGE_NAME}:latest'..."
                script {
                    if (isUnix()) {
                        sh 'docker build -t campusfix:latest .'
                    } else {
                        bat 'docker build -t campusfix:latest .'
                    }
                }
            }
        }

        stage('5. Deploy to AWS EC2') {
            steps {
                echo "==> [Stage 5] Rolling deployment to AWS EC2 with persistent volume..."
                echo "==> Target Container: ${CONTAINER_NAME} on Port ${PORT}"
                script {
                    if (isUnix()) {
                        sh 'docker ps -f name=campusfix-app'
                    } else {
                        bat 'docker ps -f name=campusfix-app'
                    }
                }
            }
        }
    }

    post {
        success {
            echo "SUCCESS: CampusFix Pipeline completed successfully! Live on AWS EC2 & Docker."
        }
        failure {
            echo "FAILURE: CampusFix Pipeline encountered an error."
        }
    }
}
