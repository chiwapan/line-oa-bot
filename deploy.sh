#!/bin/bash
# Deploy The Oasis LINE Bot to VPS
# SSH เข้า VPS แล้ว paste รันได้เลย

set -e

echo "🌿 Deploying The Oasis LINE Bot..."

# สร้าง directory
mkdir -p /opt/data/line-oa-bot
cd /opt/data/line-oa-bot

# Clone หรือ pull โค้ดล่าสุด
if [ -d ".git" ]; then
    echo "📦 Pulling latest code..."
    git pull
else
    echo "📦 Cloning from GitHub..."
    git clone https://github.com/chiwapan/line-oa-bot.git .
fi

# สร้าง .env ถ้ายังไม่มี
if [ ! -f ".env" ]; then
    echo "⚠️  สร้าง .env — ใส่ Channel Access Token ด้วย!"
    cat > .env << 'EOF'
LINE_CHANNEL_SECRET=7b9890afc2af0a629cad6fc21f332ff4
LINE_CHANNEL_ACCESS_TOKEN=
EOF
    echo "📝 แก้ไข .env: nano .env"
fi

# Build + Deploy
echo "🚀 Building and deploying..."
docker compose -f docker-compose-test.yml up -d --build

# เช็คสถานะ
echo "✅ Status:"
docker compose -f docker-compose-test.yml ps

echo ""
echo "🌐 Bot ready at: https://bot.chiwapan.online"
echo "📋 Test interface: https://bot.chiwapan.online/"
echo "🔍 Health check: https://bot.chiwapan.online/health"
echo ""
echo "📝 Logs: docker compose -f docker-compose-test.yml logs -f"
