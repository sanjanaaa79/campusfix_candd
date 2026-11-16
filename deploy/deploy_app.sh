#!/bin/bash
# ==============================================================================
# CampusFix - AWS EC2 Application Deployment Script
# Safely restarts the Docker container preserving persistent SQLite database
# ==============================================================================

set -e

APP_DIR="/home/ubuntu/campusfix"
CONTAINER_NAME="campusfix-app"
IMAGE_NAME="campusfix:latest"

echo "==> Navigating to ${APP_DIR}..."
cd "${APP_DIR}"

# Ensure data directory exists
mkdir -p "${APP_DIR}/data"

echo "==> Building fresh Docker image..."
docker build -t ${IMAGE_NAME} .

# Stop and remove existing container if running
if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
    echo "==> Stopping existing container ${CONTAINER_NAME}..."
    docker stop ${CONTAINER_NAME} || true
    docker rm ${CONTAINER_NAME} || true
fi

# Run new container with persistent database volume mounted
echo "==> Launching updated container with persistent database volume..."
docker run -d \
    --name ${CONTAINER_NAME} \
    --restart unless-stopped \
    -p 5000:5000 \
    -v "${APP_DIR}/data:/app/data" \
    --env-file "${APP_DIR}/.env" \
    ${IMAGE_NAME}

echo "==> Waiting for container to initialize..."
sleep 5

# Check container status
docker ps -f name=${CONTAINER_NAME}

echo "==> Verifying HTTP response..."
curl -f http://localhost:5000/ || { echo "Deployment failed: Healthcheck did not return HTTP 200"; exit 1; }

echo "=========================================================="
echo "  CampusFix deployed successfully on AWS EC2!            "
echo "  Access via: http://<YOUR_EC2_PUBLIC_IP>:5000           "
echo "=========================================================="
