# Configuración para Desarrollo Local

## Variables de Entorno Necesarias

Para ejecutar el servidor en local, asegúrate de tener configuradas estas variables de entorno:

```bash
ENV=local
DATABASE_URL=sqlite:///./njoy_local.db
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
```

## Cómo Ejecutar el Servidor Local

1. Asegúrate de tener las dependencias instaladas:
   ```bash
   py -m pip install -r requirements.txt
   ```

2. Ejecuta el servidor con:
   ```bash
   py run_local.py
   ```

3. El servidor estará disponible en:
   - API: http://localhost:8000
   - Documentación: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Base de Datos Local

El servidor usará SQLite por defecto en desarrollo local. La base de datos se creará automáticamente en `njoy_local.db`.

Para inicializar las tablas, visita: http://localhost:8000/init-db

## Acceso desde la Red Local (para Android)

El servidor escucha en `0.0.0.0:8000`, lo que permite:
- Acceso desde tu PC: `http://localhost:8000`
- Acceso desde dispositivos en la misma red: `http://<TU_IP_LOCAL>:8000`

Para obtener tu IP local:
```bash
ipconfig
```
Busca la dirección IPv4 de tu adaptador de red activo.
