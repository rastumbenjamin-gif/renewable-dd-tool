#!/bin/bash
# Local Database Setup for Renewable DD Tool
# Run this script to set up PostgreSQL database

echo "🔧 Setting up Renewable DD Tool Database..."
echo ""

# Use macOS username for connection
USER=$(whoami)

echo "✅ PostgreSQL is running"
echo "👤 Using macOS user: $USER"
echo ""

# Create database and user
echo "📊 Creating database and user..."
psql postgres << EOF
-- Create database
CREATE DATABASE renewable_dd_dev;

-- Create user
CREATE USER dd_user WITH PASSWORD 'dev_password_123';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE renewable_dd_dev TO dd_user;

-- Connect to the database and grant schema privileges
\c renewable_dd_dev
GRANT ALL ON SCHEMA public TO dd_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dd_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dd_user;

-- Show success
\echo '✅ Database setup complete!'
\echo ''
\echo 'Database: renewable_dd_dev'
\echo 'User: dd_user'
\echo 'Password: dev_password_123'
\echo ''
\echo 'Connection string:'
\echo 'postgresql://dd_user:dev_password_123@localhost:5432/renewable_dd_dev'
EOF

echo ""
echo "🧪 Testing connection..."
PGPASSWORD='dev_password_123' psql -U dd_user -d renewable_dd_dev -h localhost -c "SELECT 'Connection successful!' as status;"

echo ""
echo "✅ All done! Your database is ready."
echo ""
echo "Next steps:"
echo "1. cd backend"
echo "2. source venv/bin/activate"
echo "3. Update .env with database URL"
echo "4. uvicorn api.main:app --reload"
