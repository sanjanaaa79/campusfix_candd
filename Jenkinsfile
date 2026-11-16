pipeline {
    agent any

    environment {
        APP_NAME = 'campusfix'
        IMAGE_NAME = 'campusfix'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        CONTAINER_NAME = 'campusfix-app'
        PORT = '5000'
        
        // Credentials stored securely in Jenkins Credential Store:
        // 1. EC2_HOST: Secret text containing EC2 Public IP or DNS
        // 2. EC2_SSH_KEY: SSH Username with private key (Username: ubuntu)
        EC2_HOST = credentials('CAMPUSFIX_EC2_HOST')
        EC2_CRED_ID = 'CAMPUSFIX_EC2_SSH_KEY'
    }

    triggers {
        // Triggered via GitHub webhook on push, or poll SCM every 5 minutes
        githubPush()
        pollSCM('H/5 * * * *')
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('1. Checkout Source') {
            steps {
                echo "==> Pulling source code from Git repository..."
                checkout scm
            }
        }

        stage('2. Install Dependencies') {
            steps {
                echo "==> Preparing virtual environment and installing requirements..."
                sh '''
                    python3 -m venv .jenkins_venv || python -m venv .jenkins_venv
                    . .jenkins_venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('3. Run Automated Tests') {
            steps {
                echo "==> Executing Pytest test suite for Auth, RBAC & Complaints..."
                sh '''
                    . .jenkins_venv/bin/activate
                    pytest -v --tb=short
                '''
            }
        }

        stage('4. Build Docker Image') {
            steps {
                echo "==> Building Docker image '${IMAGE_NAME}:${IMAGE_TAG}' and '${IMAGE_NAME}:latest'..."
                sh '''
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        stage('5. Deploy to AWS EC2') {
            steps {
                echo "==> Deploying containerized application to AWS EC2 (${EC2_HOST})..."
                // Secure SSH authentication using Jenkins sshagent / credentials
                sshagent([EC2_CRED_ID]) {
                    sh '''
                        echo "==> Connecting to EC2 instance and executing rolling update..."
                        ssh -o StrictHostKeyChecking=no ubuntu@${EC2_HOST} << 'EOF'
                            set -e
                            
                            # 1. Ensure deployment and persistent data directories exist
                            mkdir -p ~/campusfix/data
                            
                            # 2. Check if .env exists; create default if missing
                            if [ ! -f ~/campusfix/.env ]; then
                                echo "FLASK_ENV=production" > ~/campusfix/.env
                                echo "SECRET_KEY=$(openssl rand -hex 24)" >> ~/campusfix/.env
                                echo "DATABASE_URL=sqlite:////app/data/campusfix.db" >> ~/campusfix/.env
                                echo "ADMIN_EMAIL=admin@campusfix.edu" >> ~/campusfix/.env
                                echo "ADMIN_PASSWORD=Admin@12345" >> ~/campusfix/.env
                                echo "ADMIN_NAME=Campus Administrator" >> ~/campusfix/.env
                            fi

                            # 3. Pull / load updated docker image or build directly
                            # In direct deployment mode:
                            cd ~/campusfix
                            if [ -d .git ]; then
                                git pull origin main
                                docker build -t campusfix:latest .
                            fi

                            # 4. Stop and remove existing container (if running)
                            if [ "$(docker ps -aq -f name=campusfix-app)" ]; then
                                echo "Stopping existing container..."
                                docker stop campusfix-app || true
                                docker rm campusfix-app || true
                            fi

                            # 5. Run new container with persistent volume
                            echo "Starting updated container..."
                            docker run -d \
                                --name campusfix-app \
                                --restart unless-stopped \
                                -p 5000:5000 \
                                -v ~/campusfix/data:/app/data \
                                --env-file ~/campusfix/.env \
                                campusfix:latest

                            # 6. Verify container health
                            sleep 5
                            docker ps -f name=campusfix-app
                            curl -f http://localhost:5000/ || exit 1
                            echo "==> CampusFix successfully deployed and healthy on AWS EC2!"
EOF
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "SUCCESS: CampusFix Pipeline completed successfully! Live on AWS EC2."
        }
        failure {
            echo "FAILURE: CampusFix Pipeline failed. Check console output for debug details."
        }
        always {
            // Clean up workspace test artifacts
            sh 'rm -rf .jenkins_venv'
        }
    }
}
