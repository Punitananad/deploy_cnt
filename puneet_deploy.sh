#!/bin/bash

# Puneet's Production Deployment Script
# This script pulls latest code and restarts services

echo "=========================================="
echo "  Puneet's Deployment Script"
echo "=========================================="
echo ""

# Step 1: Pull latest code from git
echo "📥 Pulling latest code from git..."
git pull origin master

if [ $? -ne 0 ]; then
    echo "❌ Git pull failed! Please check for conflicts."
    exit 1
fi

echo "✅ Code updated successfully"
echo ""

# Step 2: Check if Gunicorn is running
echo "🔍 Checking Gunicorn process..."
if pgrep -f gunicorn > /dev/null; then
    echo "✅ Gunicorn is running"
    GUNICORN_RUNNING=true
else
    echo "⚠️  Gunicorn is not running"
    GUNICORN_RUNNING=false
fi
echo ""

# Step 3: Check if Nginx is running
echo "🔍 Checking Nginx process..."
if pgrep -f nginx > /dev/null; then
    echo "✅ Nginx is running"
    NGINX_RUNNING=true
else
    echo "⚠️  Nginx is not running"
    NGINX_RUNNING=false
fi
echo ""

# Step 4: Stop existing Gunicorn processes
echo "🔄 Stopping Gunicorn processes..."
pkill -f gunicorn
sleep 2

if pgrep -f gunicorn > /dev/null; then
    echo "⚠️  Force killing remaining Gunicorn processes..."
    pkill -9 -f gunicorn
    sleep 1
fi

echo "✅ Gunicorn processes stopped"
echo ""

# Step 5: Start Gunicorn
echo "🚀 Starting Gunicorn..."
cd ~/deploy_cnt
source venv/bin/activate
nohup gunicorn -c gunicorn_config.py app:app > logs/gunicorn.log 2>&1 &

sleep 3

if pgrep -f gunicorn > /dev/null; then
    echo "✅ Gunicorn started successfully"
else
    echo "❌ Failed to start Gunicorn"
    echo "Check logs/gunicorn.log for errors"
    exit 1
fi
echo ""

# Step 6: Restart Nginx
echo "🔄 Restarting Nginx..."
sudo systemctl restart nginx

if [ $? -eq 0 ]; then
    echo "✅ Nginx restarted successfully"
else
    echo "❌ Failed to restart Nginx"
    exit 1
fi
echo ""

# Step 7: Verify services are running
echo "🔍 Verifying services..."
sleep 2

if pgrep -f gunicorn > /dev/null; then
    GUNICORN_PID=$(pgrep -f gunicorn | head -1)
    echo "✅ Gunicorn is running (PID: $GUNICORN_PID)"
else
    echo "❌ Gunicorn is not running"
fi

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx is active and running"
else
    echo "❌ Nginx failed to start"
fi

echo ""
echo "=========================================="
echo "  Deployment Complete! 🚀"
echo "=========================================="
echo ""
echo "Your app should now be running with the latest changes."
echo "Test the logout functionality to confirm the fix works."
