# 🔧 Render Deployment Fix

## Error Fixed

The error was:
```
ImportError: email-validator is not installed, run `pip install pydantic[email]`
```

**Fixed**: Added `email-validator==2.1.0` to `requirements.txt`

## Next Steps

1. **Commit and push the fix**:
   ```bash
   git add requirements.txt
   git commit -m "Add email-validator dependency"
   git push origin main
   ```

2. **Render will automatically redeploy** (if auto-deploy is enabled)

3. **Or manually redeploy**:
   - Go to Render dashboard
   - Click on your service
   - Click "Manual Deploy" → "Deploy latest commit"

## Your API URL

Once deployed, your API will be at:
- **API**: https://api-patent-alert.onrender.com
- **Docs**: https://api-patent-alert.onrender.com/docs
- **Health**: https://api-patent-alert.onrender.com/health
- **Stripe Webhook**: https://api-patent-alert.onrender.com/api/v1/billing/webhook

## Environment Variables to Set in Render

Make sure you've set these in Render dashboard → Environment:

**Required:**
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `USPTO_API_KEY` - Get from https://developer.uspto.gov
- `ADMIN_PASSWORD` - Your admin dashboard password

**Recommended:**
- `REDIS_URL` - Your Upstash Redis URL
- `DATABASE_URL` - Render provides this automatically (PostgreSQL)
- `STRIPE_SECRET_KEY` - If using billing
- `STRIPE_WEBHOOK_SECRET` - If using billing

**Optional:**
- `SMTP_USER` - For email notifications
- `SMTP_PASSWORD` - Gmail app password
- `HF_API_KEY` - For AI features
- `SENTRY_DSN` - For error tracking

## Test After Deployment

1. Check health: https://api-patent-alert.onrender.com/health
2. Check docs: https://api-patent-alert.onrender.com/docs
3. Create API key: POST to `/api/v1/auth/keys`
4. Test endpoint: GET `/api/v1/expirations` with API key

## Common Issues

**If deployment still fails:**
- Check Render logs for errors
- Verify all environment variables are set
- Make sure `DATABASE_URL` is set (Render should auto-provide this)

**If API returns 500 errors:**
- Check that `USPTO_API_KEY` is set
- Check that `SECRET_KEY` is set
- Check Render logs for specific errors

## Success! 🎉

Once deployed, you can:
- Share your API URL with clients
- Set up Stripe webhooks
- Start testing the API
- Begin acquiring customers!

