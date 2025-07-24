#!/bin/bash
set -e

echo "[*] Starting Praetor Security Hardening..."

# System update
apt update && apt upgrade -y

# Enable unattended upgrades
apt install -y unattended-upgrades
dpkg-reconfigure -flow unattended-upgrades

# UFW firewall
apt install -y ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw --force enable

# Fail2Ban
apt install -y fail2ban
systemctl enable --now fail2ban

# Auditd
apt install -y auditd
systemctl enable --now auditd

# Google Authenticator for sudo
apt install -y libpam-google-authenticator
echo "auth required pam_google_authenticator.so" >> /etc/pam.d/sudo

gocryptfs
apt install -y gocryptfs
mkdir -p ~/.vault.encrypted ~/Vault
echo "Create a secure password for your encrypted Vault:"
gocryptfs -init ~/.vault.encrypted
gocryptfs ~/.vault.encrypted ~/Vault

# Docker Hardening
if command -v docker &> /dev/null; then
  mkdir -p /etc/docker
  cat > /etc/docker/daemon.json <<EOF
{
  "live-restore": true,
  "no-new-privileges": true,
  "icc": false,
  "userns-remap": "default",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
  systemctl restart docker
fi

# Setup Praetor Hook
mkdir -p /opt/praetor/hooks /opt/praetor/logs
cp security_monitor.py /opt/praetor/hooks/
cp security_config.json /opt/praetor/

echo "[*] Praetor Security Setup Complete."
