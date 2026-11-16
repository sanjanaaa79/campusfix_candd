#!/bin/bash
# ==============================================================================
# CampusFix - AWS EC2 Automated Server Setup Script
# Target OS: Ubuntu 22.04 / 24.04 LTS on AWS EC2 (t2.micro / t3.micro)
# ==============================================================================

set -e

echo "=========================================================="
echo "  Starting CampusFix Automated AWS EC2 Environment Setup  "
echo "=========================================================="

# 1. Update and upgrade Ubuntu packages
echo "==> Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y curl git ufw apt-transport-https ca-certificates gnupg lsb-release

# 2. Install Docker CE
echo "==> Installing Docker Engine..."
if ! command -v docker &> /dev/null; then
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
else
    echo "Docker is already installed."
fi

# 3. Add 'ubuntu' user to docker group (removes sudo requirement for Docker commands)
echo "==> Adding ubuntu user to docker group..."
sudo usermod -aG docker ubuntu || true
sudo systemctl enable docker
sudo systemctl start docker

# 4. Prepare application directory & persistent database storage
APP_DIR="/home/ubuntu/campusfix"
echo "==> Preparing application directory at ${APP_DIR}..."
mkdir -p "${APP_DIR}/data"

# 5. Generate production .env configuration if not already present
if [ ! -f "${APP_DIR}/.env" ]; then
    echo "==> Generating production .env file with secure secret key..."
    SECRET_KEY=$(openssl rand -hex 32)
    cat <<EOF > "${APP_DIR}/.env"
FLASK_ENV=production
FLASK_DEBUG=0
PORT=5000
SECRET_KEY=${SECRET_KEY}
DATABASE_URL=sqlite:////app/data/campusfix.db
ADMIN_NAME=Campus Administrator
ADMIN_EMAIL=admin@campusfix.edu
ADMIN_PASSWORD=Admin@12345
EOF
    echo ".env created successfully."
else
    echo ".env already exists. Preserving existing configuration."
fi

# 6. Configure UFW firewall (allow SSH, HTTP, and CampusFix Port 5000)
echo "==> Configuring firewall rules..."
sudo ufw allow 22/tcp || true
sudo ufw allow 80/tcp || true
sudo ufw allow 5000/tcp || true
# Note: Ensure AWS EC2 Security Group also allows Port 22 and Port 5000 from Anywhere (0.0.0.0/0)

echo "=========================================================="
echo "  EC2 Server Setup Completed Successfully!               "
echo "  You can now deploy CampusFix using Docker or Jenkins.  "
echo "=========================================================="
