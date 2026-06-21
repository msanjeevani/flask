#!/bin/bash

# CareMesh Monitoring Script

echo "📊 CareMesh System Monitoring"
echo "============================="

# Check Docker services
echo ""
echo "🐳 Docker Services:"
docker-compose ps

echo ""
echo "📈 Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

echo ""
echo "🗄️  Database Status:"
if docker-compose exec -T postgres pg_isready -U caremesh_user > /dev/null 2>&1; then
    echo "✅ PostgreSQL: Connected"
    
    # Get database size
    DB_SIZE=$(docker-compose exec -T postgres psql -U caremesh_user -d caremesh -t -c "SELECT pg_size_pretty(pg_database_size('caremesh'))" | tr -d '[:space:]')
    echo "   Database size: $DB_SIZE"
    
    # Get row counts
    echo "   Row counts:"
    docker-compose exec -T postgres psql -U caremesh_user -d caremesh -t -c "
        SELECT 'hospitals: ' || COUNT(*) FROM hospitals
        UNION ALL
        SELECT 'users: ' || COUNT(*) FROM users
        UNION ALL
        SELECT 'cases: ' || COUNT(*) FROM cases
        UNION ALL
        SELECT 'treatments: ' || COUNT(*) FROM treatments
    " | sed 's/^/     /'
else
    echo "❌ PostgreSQL: Not connected"
fi

echo ""
echo "🧠 Cache Status:"
if docker-compose exec -T redis redis-cli -a redis_password ping > /dev/null 2>&1; then
    echo "✅ Redis: Connected"
    
    # Get Redis info
    INFO=$(docker-compose exec -T redis redis-cli -a redis_password info)
    echo "   Memory used: $(echo "$INFO" | grep 'used_memory_human' | cut -d: -f2)"
    echo "   Connected clients: $(echo "$INFO" | grep 'connected_clients' | cut -d: -f2)"
else
    echo " Redis: Not connected"
fi

echo ""
echo " API Health Check:"
if curl -s http://localhost:5000/api/health > /dev/null; then
    HEALTH=$(curl -s http://localhost:5000/api/health)
    echo " API: Healthy"
    echo "   Environment: $(echo $HEALTH | jq -r '.environment')"
    echo "   Database: $(echo $HEALTH | jq -r '.database')"
else
    echo " API: Unreachable"
fi

echo ""
echo " Disk Usage:"
echo "   Uploads: $(du -sh uploads 2>/dev/null | cut -f1)"
echo "   Logs: $(du -sh logs 2>/dev/null | cut -f1)"
echo "   Models: $(du -sh models 2>/dev/null | cut -f1)"

echo ""
echo " Recent Logs (last 5 errors):"
docker-compose logs --tail=20 backend | grep -i error | tail -5

echo ""
echo " Alerts:"
# Check for services down
if ! docker-compose ps | grep -q "Up (healthy)"; then
    echo " Some services are not healthy"
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "  Disk usage is high: $DISK_USAGE%"
fi

# Check memory usage
MEM_FREE=$(free -m | awk 'NR==2 {print $4}')
if [ $MEM_FREE -lt 100 ]; then
    echo "  Low memory: ${MEM_FREE}MB free"
fi

echo ""
echo " Monitoring complete at $(date)"