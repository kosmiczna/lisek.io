#!/bin/bash
cd /root/lisek.io
OLD=$(git rev-parse HEAD)
git pull -q
NEW=$(git rev-parse HEAD)

if [ "$OLD" != "$NEW" ]; then
    ./venv/bin/pip install -q -r requirements.txt
    systemctl restart lisek.io
fi
