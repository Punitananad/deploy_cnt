# CalculatenTrade - Clean Project Structure

## 🎯 Core Application Files

### Main Application
- **app.py** - Main Flask application with all routes and configurations
- **journal.py** - Trading journal blueprint with advanced features
- **admin_blueprint.py** - Admin panel for user and system management
- **mentor.py** - Mentor system for referral management
- **employee_dashboard_bp.py** - Employee dashboard for user management
- **multi_broker_system.py** - Multi-broker integration (Kite, Dhan, Angel One)

### Configuration & Services
- **database_config.py** - PostgreSQL database configuration
- **email_service.py** - Dual email service (user + admin emails)
- **subscription_models.py** - Subscription and payment models
- **subscription_admin.py** - Subscription management admin panel
- **broker_session_model.py** - Broker session management
- **broker_integration.py** - Broker API integration utilities
- **toast_utils.py** - Toast notification system
- **token_store.py** - Token storage and management

## 📁 Directory Structure

```
clean/
├── static/                    # Static assets (CSS, JS, images)
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript files
│   ├── favicons/             # Favicon files
│   └── profile_pics/         # User profile pictures
├── templates/                # Jinja2 templates
│   ├── admin/               # Admin panel templates
│   ├── employee_dashboard/  # Employee dashboard templates
│   ├── mentor/              # Mentor system templates
│   └── *.html              # Main application templates
├── uploads/                 # File uploads
│   └── mistakes/           # Mistake attachments
├── migrations/             # Database migrations
├── logs/                   # Application logs (auto-created)
├── instance/              # Flask instance folder (auto-created)
└── .ebextensions/         # AWS Elastic Beanstalk configuration
```

## 🔧 Configuration Files

- **.env** - Environment variables (keep secure)
- **.env.example** - Example environment file
- **requirements.txt** - Python dependencies (original)
- **requirements_clean.txt** - Clean essential dependencies
- **client_secret.json** - Google OAuth credentials (keep secure)
- **dhan_token.json** - Dhan API token (keep secure)
- **render.yaml** - Render.com deployment configuration

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements_clean.txt
   ```

2. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Initialize Database**
   ```bash
   python setup_dev.py
   ```

4. **Run Application**
   ```bash
   python app.py
   ```

5. **Access Application**
   - Main App: http://localhost:5000
   - Admin Panel: http://localhost:5000/admin
   - Employee Dashboard: http://localhost:5000/employee
   - Mentor Panel: http://localhost:5000/mentor

## 🎨 Features

### 🧮 Trading Calculators
- Intraday Calculator (5x leverage)
- Delivery Calculator (long-term equity)
- Swing Calculator (medium-term trading)
- MTF Calculator (Margin Trading Facility)
- F&O Calculator (Futures & Options)

### 📊 Trade Management
- Position saving and management
- Position splitting with multiple SL/targets
- Real-time market data (Dhan API)
- Pivot point calculations
- Risk-reward analysis

### 📝 Trading Journal
- Comprehensive trade logging
- Strategy management
- Performance analytics
- Mistake tracking
- Rule-based trading system

### 🔐 Authentication
- Email/Password with OTP verification
- Google OAuth 2.0 integration
- Secure session management
- Password reset functionality

### 👥 Multi-User System
- User management
- Admin dashboard
- Employee access controls
- Mentor referral system
- Role-based permissions

### 🔗 Multi-Broker Integration
- Zerodha Kite Connect
- Dhan HQ API
- Angel One SmartAPI
- Session management
- Real-time data sync

## 🛡️ Security Features

- Environment-based configuration
- Secure session management
- OTP-based verification
- Rate limiting
- SQL injection protection
- XSS protection

## 📈 Subscription System

- Monthly/Yearly plans
- Coupon system
- Mentor commissions
- Payment integration (Razorpay)
- Subscription analytics

## 🔄 Database

- PostgreSQL primary database
- Flask-Migrate for schema management
- Optimized queries
- Connection pooling
- Backup-ready structure

## 📱 Frontend

- Responsive Bootstrap design
- Mobile-optimized interface
- Real-time updates
- Toast notifications
- Progressive Web App features

## 🚀 Deployment Ready

- Environment-based configuration
- Docker support (via render.yaml)
- AWS Elastic Beanstalk ready
- Render.com deployment configuration
- Production-optimized settings

---

**Made with ❤️ for traders by traders**