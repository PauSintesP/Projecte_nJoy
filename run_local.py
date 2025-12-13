#!/usr/bin/env python3
"""
Script para ejecutar el servidor FastAPI en modo desarrollo local
Usa uvicorn con recarga automática para desarrollo rápido
"""
import uvicorn

if __name__ == "__main__":
    print("🚀 Iniciando servidor FastAPI en modo desarrollo...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🔄 Auto-reload activado - los cambios se aplicarán automáticamente\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Permite conexiones desde la red local (para Android)
        port=8000,
        reload=True,      # Recarga automática al guardar cambios
        log_level="info"
    )
