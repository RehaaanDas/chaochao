#!/bin/bash
chmod +x /home/pi/chaochao/launch.sh
echo "launch.sh up"
/home/pi/chaochao/ccenv/bin/python3 -m http.server 8001 --bind 0.0.0.0 --directory /home/pi/chaochao &
/home/pi/chaochao/ccenv/bin/python3 /home/pi/chaochao/server.py &
/usr/bin/npx localtunnel --port 8001 --subdomain chaochao &
/usr/bin/npx localtunnel --port 8002 --subdomain chaochaows
