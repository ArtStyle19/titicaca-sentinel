#!/bin/bash
# Script de inicio completo para Titicaca Sentinel

echo "🚀 Iniciando Titicaca Sentinel..."
echo ""

# Limpiar puerto 8000
echo "🧹 Limpiando puerto 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 2

# Iniciar backend
echo "🔵 Iniciando backend..."
cd /home/vicari/Downloads/PROJECTS/titicaca-sentinel
nohup ./start_backend.sh > backend.log 2>&1 &
BACKEND_PID=$!

# Esperar a que el backend esté listo
echo "⏳ Esperando a que el backend esté listo..."
for i in {1..15}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend activo en puerto 8000"
        break
    fi
    echo "   Esperando... ($i/15)"
    sleep 2
done

# Verificar health
HEALTH=$(curl -s http://localhost:8000/health 2>&1)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Backend saludable"
else
    echo "❌ Backend no responde correctamente"
    echo "$HEALTH"
    exit 1
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  TITICACA SENTINEL - SISTEMA LISTO                       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Backend: http://localhost:8000"
echo "🌐 Docs API: http://localhost:8000/docs"
echo ""
echo "Para iniciar el frontend:"
echo "  ./start_frontend.sh"
echo ""
echo "Para ver logs del backend:"
echo "  tail -f backend.log"
echo ""
