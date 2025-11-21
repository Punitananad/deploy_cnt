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

# Step 4: Restart Gunicorn
echo "🔄 Restarting Gunicorn..."
sudo systemctl restart gunicorn

if [ $? -eq 0 ]; then
    echo "✅ Gunicorn restarted successfully"
else
    echo "❌ Failed to restart Gunicorn"
    exit 1
fi
echo ""

# Step 5: Restart Nginx
echo "🔄 Restarting Nginx..."
sudo systemctl restart nginx

if [ $? -eq 0 ]; then
    echo "✅ Nginx restarted successfully"
else
    echo "❌ Failed to restart Nginx"
    exit 1
fi
echo ""

# Step 6: Verify services are running
echo "🔍 Verifying services..."
sleep 2

if systemctl is-active --quiet gunicorn; then
    echo "✅ Gunicorn is active and running"
else
    echo "❌ Gunicorn failed to start"
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
