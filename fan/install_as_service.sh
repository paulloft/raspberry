#!/bin/bash
if [[ $EUID -ne 0 ]]; then
   echo "Installing must be run as root" 1>&2
   exit 1
fi

CUR_DIR="$(pwd)"
echo "Install cooling control service"
chmod a+x $CUR_DIR/cooling.py
mkdir -p /usr/src/fan/ && ln -s $CUR_DIR/cooling.py "$_"
cat > /lib/systemd/system/cooling.service <<EOF
[Unit]
Description=Cooling fan control

[Service]
User=root
Group=root
Type=simple
ExecStart=/usr/bin/python /usr/src/fan/cooling.py
Restart=Always

[Install]
WantedBy=multi-user.target
EOF
echo "..."

systemctl daemon-reload 
systemctl enable cooling.service
service cooling start
echo "Instaling complete"