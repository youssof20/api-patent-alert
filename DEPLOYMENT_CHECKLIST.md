# Production Deployment Checklist

## Pre-Deployment

### 1. Environment Configuration
- [ ] Copy `.env.production` to `.env`
- [ ] Generate secure `SECRET_KEY` (32+ random characters)
- [ ] Set strong `ADMIN_PASSWORD` (12+ characters)
- [ ] Get `USPTO_API_KEY` from https://developer.uspto.gov
- [ ] Setup Redis (Upstash free tier recommended)
- [ ] Configure Stripe keys (test mode first)
- [ ] Setup email SMTP (Gmail app password)

### 2. Database Setup
- [ ] Run migrations: `python -m alembic upgrade head`
- [ ] Verify database connection
- [ ] Test creating API key

### 3. Testing
- [ ] Test all endpoints locally
- [ ] Verify webhook scheduler starts
- [ ] Test admin dashboard login
- [ ] Verify email sending (if configured)

## Deployment Steps

### Render.com (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Production ready"
   git push origin main
   ```

2. **Create Render Service**
   - Go to https://render.com
   - New → Web Service
   - Connect GitHub repo
   - Use `render.yaml` configuration

3. **Set Environment Variables**
   - Copy all values from `.env` to Render dashboard
   - **Important**: Set `ENVIRONMENT=production`
   - Set `DATABASE_URL` (Render provides PostgreSQL)

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Check logs for errors

5. **Post-Deployment**
   - Test `/health` endpoint
   - Test API key creation
   - Verify scheduler is running (check logs)
   - Test webhook registration

### Other Platforms

**Heroku:**
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
git push heroku main
```

**Docker:**
```bash
docker build -t patent-alert-api .
docker run -p 8000:8000 --env-file .env patent-alert-api
```

## Post-Deployment Verification

### Health Checks
- [ ] `/health` returns 200
- [ ] `/api/v1/monitoring/health/detailed` shows all services healthy
- [ ] Background scheduler is running (check logs)

### Functional Tests
- [ ] Create API key via `/api/v1/auth/keys`
- [ ] Query `/api/v1/expirations` with API key
- [ ] Register webhook via `/api/v1/webhooks`
- [ ] Check usage stats via `/api/v1/stats`
- [ ] Admin dashboard login works

### Monitoring
- [ ] Check `/api/v1/monitoring/metrics` for performance
- [ ] Verify error tracking (Sentry if configured)
- [ ] Monitor response times
- [ ] Check Redis connection

## Production Hardening

### Security
- [ ] Change default `ADMIN_PASSWORD`
- [ ] Use strong `SECRET_KEY` (32+ random chars)
- [ ] Enable HTTPS (automatic on Render/Heroku)
- [ ] Review CORS settings
- [ ] Restrict admin endpoints (add IP whitelist if needed)

### Performance
- [ ] Enable Redis for caching
- [ ] Monitor response times
- [ ] Set up database connection pooling
- [ ] Configure CDN if needed

### Monitoring
- [ ] Setup Sentry for error tracking
- [ ] Configure uptime monitoring (UptimeRobot)
- [ ] Set up email alerts for errors
- [ ] Monitor API usage and costs

## Support Setup

- [ ] Update contact email in all documentation
- [ ] Setup support email forwarding
- [ ] Create status page (optional)
- [ ] Document API changes/versions

## Next: Start Acquiring Clients

See `NEXT_STEPS.md` for marketing and sales guidance.

