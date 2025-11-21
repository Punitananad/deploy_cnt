-- SQL Script to Create Missing Tables
-- Run this directly in your PostgreSQL database if Python scripts fail

-- Users table (CRITICAL)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    coupon_code VARCHAR(50),
    registered_on TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    google_id VARCHAR(100) UNIQUE,
    profile_pic VARCHAR(200),
    name VARCHAR(100),
    subscription_active BOOLEAN NOT NULL DEFAULT FALSE,
    subscription_expires TIMESTAMP WITH TIME ZONE,
    subscription_type VARCHAR(20)
);

-- User Settings
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    email_notifications BOOLEAN DEFAULT TRUE,
    theme VARCHAR(20) DEFAULT 'light',
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    default_calculator VARCHAR(20) DEFAULT 'intraday',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reset OTP
CREATE TABLE IF NOT EXISTS reset_otp (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) NOT NULL,
    otp_hash VARCHAR(128) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    attempts INTEGER DEFAULT 0 NOT NULL,
    used BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Swing Trades (MISSING)
CREATE TABLE IF NOT EXISTS swing_trades (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    trade_type VARCHAR(10) NOT NULL DEFAULT 'buy',
    avg_price FLOAT NOT NULL,
    quantity INTEGER NOT NULL,
    expected_return FLOAT,
    risk_percent FLOAT,
    capital_used FLOAT,
    target_price FLOAT,
    stop_loss_price FLOAT,
    total_reward FLOAT,
    total_risk FLOAT,
    rr_ratio FLOAT,
    symbol VARCHAR(50),
    comment VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Trade Splits
CREATE TABLE IF NOT EXISTS trade_splits (
    id SERIAL PRIMARY KEY,
    trade_id INTEGER NOT NULL,
    trade_type VARCHAR(20) NOT NULL,
    preview VARCHAR(100) NOT NULL,
    qty INTEGER NOT NULL,
    sl_price FLOAT NOT NULL,
    target_price FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Preview Templates
CREATE TABLE IF NOT EXISTS preview_templates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    instrument VARCHAR(50) NOT NULL,
    strike VARCHAR(20),
    payload JSON NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Strategies (Journal)
CREATE TABLE IF NOT EXISTS strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trades (Journal)
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    entry_price FLOAT NOT NULL,
    exit_price FLOAT,
    quantity INTEGER NOT NULL,
    date DATE NOT NULL,
    result VARCHAR(20),
    pnl FLOAT DEFAULT 0,
    notes TEXT,
    trade_type VARCHAR(10) DEFAULT 'long',
    risk FLOAT DEFAULT 0,
    reward FLOAT DEFAULT 0,
    strategy_id INTEGER REFERENCES strategies(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Rules (Journal)
CREATE TABLE IF NOT EXISTS rules (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subscription Plans
CREATE TABLE IF NOT EXISTS subscription_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    price_monthly INTEGER NOT NULL,
    price_yearly INTEGER NOT NULL,
    features JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Subscriptions
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    plan_id INTEGER REFERENCES subscription_plans(id) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    payment_id INTEGER REFERENCES payments(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subscription History
CREATE TABLE IF NOT EXISTS subscription_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    subscription_id INTEGER REFERENCES user_subscriptions(id) NOT NULL,
    action VARCHAR(50) NOT NULL,
    details JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Mentor
CREATE TABLE IF NOT EXISTS mentor (
    id SERIAL PRIMARY KEY,
    display_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    commission_rate FLOAT DEFAULT 40.0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Coupon
CREATE TABLE IF NOT EXISTS coupon (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_percent FLOAT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    mentor_id INTEGER REFERENCES mentor(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Employee
CREATE TABLE IF NOT EXISTS employee (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'employee',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_swing_trades_user_id ON swing_trades(user_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_date ON trades(date);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_coupon_code ON coupon(code);

-- Insert default data
INSERT INTO subscription_plans (name, display_name, description, price_monthly, price_yearly) 
VALUES 
    ('monthly', 'Monthly Plan', 'Monthly subscription', 30000, 0),
    ('yearly', 'Yearly Plan', 'Yearly subscription with discount', 0, 79900)
ON CONFLICT (name) DO NOTHING;

INSERT INTO strategies (name, description) 
VALUES 
    ('Breakout', 'Breakout trading strategy'),
    ('Swing', 'Swing trading strategy'),
    ('Scalping', 'Short-term scalping strategy')
ON CONFLICT DO NOTHING;

COMMIT;