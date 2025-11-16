# Production Deployment Guide

This guide covers production-specific configurations and best practices for deploying the PII Redaction WebApp.

## Production Configuration

The application is now configured to run in production mode with:

- ✅ **Gunicorn WSGI Server** - Production-grade Python web server
- ✅ **Eventlet Workers** - Async support for Flask-SocketIO
- ✅ **Optimized Logging** - Reduced logging in production
- ✅ **Health Checks** - `/health` endpoint for monitoring
- ✅ **Environment Variables** - Configurable settings

## Quick Production Start

### Using Docker Compose (Recommended)

```bash
cd PII-Redaction-WebApp
docker-compose up --build -d
```

The application will automatically run in production mode.

### Manual Production Start

```bash
cd backend
gunicorn --config gunicorn_config.py wsgi:application
```

## Production Environment Variables

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `FLASK_HOST` | `0.0.0.0` | Host to bind server |
| `FLASK_PORT` | `5000` | Port to run server |
| `LOG_LEVEL` | `info` | Logging level (debug/info/warning/error) |
| `PYTHONUNBUFFERED` | `1` | Disable Python output buffering |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `http://localhost:5000` | Backend API URL |

## Production Checklist

### Security

- [ ] Enable HTTPS/SSL certificates
- [ ] Configure CORS properly (restrict origins in production)
- [ ] Set secure environment variables
- [ ] Enable rate limiting
- [ ] Configure firewall rules
- [ ] Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
- [ ] Regular security updates

### Performance

- [ ] Use reverse proxy (Nginx/Traefik) in front of application
- [ ] Enable gzip compression
- [ ] Configure CDN for static assets
- [ ] Set up caching strategy
- [ ] Monitor resource usage (CPU, memory, disk)
- [ ] Configure auto-scaling if needed

### Monitoring

- [ ] Set up application monitoring (New Relic, Datadog, etc.)
- [ ] Configure log aggregation (ELK, CloudWatch, etc.)
- [ ] Set up error tracking (Sentry, Rollbar)
- [ ] Configure health check monitoring
- [ ] Set up alerts for critical issues

### Backup & Recovery

- [ ] Regular database backups (if using database)
- [ ] Backup configuration files
- [ ] Document recovery procedures
- [ ] Test backup restoration

## Production Deployment Examples

### With Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/pii-redaction
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Backend
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Frontend (if serving from same server)
    location /static {
        alias /path/to/frontend/build;
    }
}
```

### Docker Compose with Production Overrides

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    environment:
      - FLASK_ENV=production
      - LOG_LEVEL=warning
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  frontend:
    environment:
      - REACT_APP_API_URL=https://api.your-domain.com
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Performance Tuning

### Gunicorn Workers

For Flask-SocketIO, use 1 worker with eventlet. For higher throughput without WebSockets, you can use multiple workers:

```python
# gunicorn_config.py
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"  # Only if not using SocketIO
```

### Resource Limits

Set appropriate resource limits in Docker:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      cpus: '1'
      memory: 2G
```

## Troubleshooting Production Issues

### High Memory Usage

- Check for memory leaks
- Reduce worker count
- Monitor with `docker stats`

### Slow Response Times

- Check database queries (if using database)
- Enable caching
- Use CDN for static assets
- Monitor network latency

### WebSocket Connection Issues

- Ensure reverse proxy supports WebSockets
- Check firewall rules
- Verify CORS settings

### Logs

View production logs:
```bash
# Docker
docker-compose logs -f backend

# Gunicorn
tail -f /var/log/gunicorn/error.log
```

## Security Best Practices

1. **Never commit secrets** - Use environment variables or secrets management
2. **Keep dependencies updated** - Regularly update Python packages
3. **Use HTTPS** - Always use SSL/TLS in production
4. **Restrict CORS** - Don't use `*` in production, specify allowed origins
5. **Rate limiting** - Implement rate limiting to prevent abuse
6. **Input validation** - Validate all user inputs
7. **Error handling** - Don't expose sensitive information in error messages

## Monitoring Endpoints

- **Health Check**: `GET /health`
  - Returns: `{"status": "healthy", "service": "PII Redaction API"}`

## Support

For production issues, check:
1. Application logs
2. System resources (CPU, memory, disk)
3. Network connectivity
4. Health check endpoint

