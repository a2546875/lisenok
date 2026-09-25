#!/bin/bash
set -e
rm -f /etc/nginx/sites-enabled/default
ln -sfn /etc/nginx/sites-available/lisenok /etc/nginx/sites-enabled/lisenok
cp /opt/lisenok/deploy/lisenok.service /etc/systemd/system/lisenok.service
cp /opt/lisenok/deploy/lisenok-admin.service /etc/systemd/system/lisenok-admin.service
nginx -t
systemctl daemon-reload
systemctl enable --now lisenok
systemctl enable --now lisenok-admin
systemctl enable --now nginx
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
sleep 2
systemctl is-active lisenok
systemctl is-active lisenok-admin
systemctl is-active nginx
curl -sS http://127.0.0.1:8000/api/health
echo
curl -sS -o /dev/null -w "public:%{http_code}\n" http://127.0.0.1/
curl -sS -o /dev/null -w "asset:%{http_code}\n" http://127.0.0.1/assets/forest-bg.png
