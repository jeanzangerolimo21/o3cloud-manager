#!/usr/bin/env bash
set -euo pipefail

cd /opt/o3cloud-manager

install -o root -g root -m 0644 deployment/o3cloud-manager.service /etc/systemd/system/o3cloud-manager.service
chown -R o3cloud:o3cloud /opt/o3cloud-manager/logs
chmod 0750 /opt/o3cloud-manager/logs
find /opt/o3cloud-manager/logs -type f -name "*.log" -exec chown o3cloud:o3cloud {} + -exec chmod 0640 {} +

systemctl daemon-reload
systemctl enable o3cloud-manager.service
systemctl restart o3cloud-manager.service
systemctl status o3cloud-manager.service --no-pager
