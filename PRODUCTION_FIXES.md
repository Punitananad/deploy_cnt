# Production Deployment Fixes for CalculatenTrade

## 🚨 Critical Issues Causing 500 Error

### 1. Environment Configuration Conflicts
**Problem**: Your `.env` file has conflicting settings:
```env
FLASK_ENV=production  # Line 2
FLASK_ENV=development # Line 25 (CONFLICT!)
```

**Fix**: Remove the duplicate and keep only:
```env
FLASK_ENV=production
```

### 2. Database Configuration Issues
**Problem**: Your app expects production PostgreSQL but may not be connecting properly.

**Fix**: Update your `.env` with proper production database settings:
```env
DATABASE_TYPE=postgres
# Use either full DATABASE_URL (recommended):
DATABASE_URL=postgresql://username:password@your-db-host:5432/calculatentrade_db?sslmode=require&connect_timeout=10

# OR individual components:
DB_HOST=your-production-db-host
DB_PORT=5432
DB_NAME=calculatentrade_db
DB_USER=your-db-username
DB_PASSWORD=your-secure-db-password
```

### 3. Missing Production Security Settings
**Fix**: Add these to your `.env`:
```env
FORCE_HTTPS=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=None
SESSION_COOKIE_DOMAIN=.calculatentrade.com
```

### 4. Google OAuth Configuration
**Problem**: OAuth might fail due to incorrect redirect URIs.

**Fix**: Ensure your Google Cloud Console has these redirect URIs:
- `https://calculatentrade.com/auth/google/callback`
- `https://www.calculatentrade.com/auth/google/callback`

## 🔧 Step-by-Step Production Fix

### Step 1: Update Your .env File
Replace your current `.env` with this production-ready version:

```env
# Flask Configuration
FLASK_SECRET=stable-oauth-secret-key-2024-persistent-sessions
FLASK_ENV=production
SESSION_PERMANENT_LIFETIME=2592000

# Production Security
FORCE_HTTPS=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_SAMESITE=None
SESSION_COOKIE_DOMAIN=.calculatentrade.com

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email Configuration
ADMIN_MAIL_USERNAME=your-admin-email@gmail.com
ADMIN_MAIL_PASSWORD=your-admin-app-password
USER_MAIL_USERNAME=your-user-email@gmail.com
USER_MAIL_PASSWORD=your-user-app-password

# Database - REPLACE WITH YOUR PRODUCTION DB
DATABASE_TYPE=postgres
DATABASE_URL=postgresql://your-db-user:your-db-password@your-production-db-host:5432/calculatentrade_db?sslmode=require&connect_timeout=10

# Razorpay
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# Dhan API
DHAN_CLIENT_ID=1107798386
DHAN_ACCESS_TOKEN=your-real-dhan-token

# Admin Key
ADMIN_KEY=stable-oauth-secret-key-2024-persistent-sessions

# SMTP Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USE_SSL=false
SMTP_TIMEOUT=20
```

### Step 2: Database Setup
1. **Ensure your production PostgreSQL database is running**
2. **Create the database if it doesn't exist**:
   ```sql
   CREATE DATABASE calculatentrade_db;
   ```
3. **Run database migrations**:
   ```bash
   flask db upgrade
   ```

### Step 3: Check Required Files
Ensure these files exist in your production environment:
- `client_secret.json` (for Google OAuth)
- All template files in `templates/` directory
- All static files in `static/` directory

### Step 4: Test the Fix
1. **Restart your application server**
2. **Check the logs for any remaining errors**
3. **Test the URL**: https://calculatentrade.com/calculatentrade_journal/dashboard

## 🐛 Common 500 Error Causes

### Database Connection Issues
```python
# Check if your database is accessible
import psycopg2
try:
    conn = psycopg2.connect(
        host="your-db-host",
        database="calculatentrade_db", 
        user="your-db-user",
        password="your-db-password"
    )
    print("Database connection successful!")
    conn.close()
except Exception as e:
    print(f"Database connection failed: {e}")
```

### Missing Environment Variables
The app will crash if these are missing:
- `FLASK_SECRET`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `DB_PASSWORD` (if using individual DB components)

### File Permissions
Ensure your web server can read:
- `.env` file
- `client_secret.json`
- All template and static files

## 🚀 Production Deployment Checklist

- [ ] Remove `FLASK_ENV=development` duplicate
- [ ] Set `FLASK_ENV=production`
- [ ] Configure production database connection
- [ ] Add production security settings
- [ ] Verify Google OAuth redirect URIs
- [ ] Ensure `client_secret.json` exists
- [ ] Test database connectivity
- [ ] Check file permissions
- [ ] Restart application server
- [ ] Monitor logs for errors

## 📞 If Issues Persist

1. **Check application logs** for specific error messages
2. **Verify database connectivity** from your production server
3. **Test Google OAuth** redirect URIs in Google Cloud Console
4. **Ensure all required Python packages** are installed in production
5. **Check web server configuration** (nginx/apache) for proper proxy settings

## 🔍 Debug Commands

```bash
# Check if environment variables are loaded
python -c "import os; print('FLASK_ENV:', os.getenv('FLASK_ENV'))"

# Test database connection
python -c "from database_config import get_postgres_url; print(get_postgres_url())"

# Check if all required files exist
ls -la client_secret.json
ls -la .env
```

The main issue is likely the conflicting `FLASK_ENV` settings in your `.env` file. Fix that first, then update your database configuration for production.