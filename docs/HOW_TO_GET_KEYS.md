# 🔑 How to Get Each .env Key - Step-by-Step Guide

## ✅ REQUIRED (Must Fill In)

### 1. `SECRET_KEY`
**What it is**: Secret key for encryption and security  
**How to get it**:
```bash
# Run this command in your terminal:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
**Copy the output** and paste it as your `SECRET_KEY`  
**Example**: `xK9mP2qL8vN4rT6wY1zA3bC5dE7fG9hI0jK2lM4nO6pQ8rS0tU2vW4xY6zA8bC0dE`

---

### 2. `USPTO_API_KEY`
**What it is**: API key to access USPTO patent data (REQUIRED for the API to work)  
**How to get it**:
1. Go to: https://developer.uspto.gov
2. Click "Sign Up" or "Login"
3. Create an account (free)
4. Go to "API Keys" or "My Applications"
5. Click "Create New API Key"
6. Copy the API key
7. Paste it as `USPTO_API_KEY=your_key_here`

**Note**: It may take a few minutes to activate after creation

---

### 3. `ADMIN_PASSWORD`
**What it is**: Password for admin dashboard login  
**How to get it**: **You create it yourself!**
- Choose a strong password (12+ characters)
- Mix of letters, numbers, and symbols
- Example: `MySecurePass123!@#`
- Set: `ADMIN_PASSWORD=MySecurePass123!@#`

---

## ⚙️ OPTIONAL BUT RECOMMENDED

### 4. `REDIS_URL`
**What it is**: Redis connection for caching and rate limiting  
**Options**:

**Option A: Local Redis (Development)**
- Install Redis: https://redis.io/download
- Or use Docker: `docker run -d -p 6379:6379 redis`
- Use: `REDIS_URL=redis://localhost:6379/0`

**Option B: Upstash (Free Cloud Redis - Recommended)**
1. Go to: https://upstash.com
2. Sign up (free)
3. Click "Create Database"
4. Choose "Global" or "Regional"
5. **IMPORTANT**: Look for "Redis URL" or "Connection String" (NOT REST API)
6. Copy the "Redis URL" (format: `redis://default:password@endpoint.upstash.io:6379`)
7. Paste as: `REDIS_URL=redis://default:password@endpoint.upstash.io:6379`
8. **Note**: If you only see REST API credentials, see `UPSTASH_REDIS_SETUP.md` for help

**Option C: Redis Cloud**
1. Go to: https://redis.com/cloud
2. Sign up for free tier
3. Create database
4. Copy connection string
5. Paste as `REDIS_URL`

**Note**: App works without Redis, but caching/rate limiting will be disabled

---

### 5. `STRIPE_SECRET_KEY` (For Billing)
**What it is**: Stripe API key for payment processing  
**How to get it**:
1. Go to: https://stripe.com
2. Sign up for account (free)
3. Go to Dashboard → Developers → API keys
4. Copy "Secret key" (starts with `sk_test_` for test mode)
5. Paste as: `STRIPE_SECRET_KEY=sk_test_your_key_here`

**For Production**: Use live keys (starts with `sk_live_`)

---

### 6. `STRIPE_PUBLISHABLE_KEY` (For Billing)
**What it is**: Public Stripe key for frontend  
**How to get it**:
1. Same Stripe dashboard as above
2. Copy "Publishable key" (starts with `pk_test_`)
3. Paste as: `STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here`

---

### 7. `STRIPE_WEBHOOK_SECRET` (For Billing)
**What it is**: Secret to verify Stripe webhooks  
**How to get it**:
1. In Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://your-domain.com/api/v1/billing/webhook`
4. Select events: `customer.subscription.*`, `invoice.*`
5. After creating, click on the webhook
6. Copy "Signing secret" (starts with `whsec_`)
7. Paste as: `STRIPE_WEBHOOK_SECRET=whsec_your_secret_here`

**Note**: Only needed if you're using Stripe billing

---

### 8. `SMTP_USER` (For Email Notifications)
**What it is**: Email address for sending emails  
**How to get it**: Use your Gmail address
- Set: `SMTP_USER=your_email@gmail.com`

---

### 9. `SMTP_PASSWORD` (For Email Notifications)
**What it is**: Gmail app password (NOT your regular password)  
**How to get it**:
1. Go to: https://myaccount.google.com
2. Enable 2-Factor Authentication (required)
3. Go to: https://myaccount.google.com/apppasswords
4. Select "Mail" and "Other (Custom name)"
5. Name it: "Patent Alert API"
6. Click "Generate"
7. Copy the 16-character password (no spaces)
8. Paste as: `SMTP_PASSWORD=abcdefghijklmnop`

**Note**: If you don't see app passwords, enable 2FA first

---

### 10. `FROM_EMAIL` (For Email Notifications)
**What it is**: Email address shown as sender  
**How to get it**: Usually same as `SMTP_USER`
- Set: `FROM_EMAIL=your_email@gmail.com`
- Or use: `FROM_EMAIL=noreply@yourdomain.com` (if you have custom domain)

---

### 11. `HF_API_KEY` (For AI Summarization - Optional)
**What it is**: Hugging Face API key for AI features  
**How to get it**:
1. Go to: https://huggingface.co
2. Sign up (free)
3. Go to: https://huggingface.co/settings/tokens
4. Click "New token"
5. Name it: "Patent Alert API"
6. Select "Read" permission
7. Copy the token
8. Paste as: `HF_API_KEY=your_token_here`

**Note**: Optional - app works without it (AI features disabled)

---

### 12. `SENTRY_DSN` (For Error Tracking - Optional)
**What it is**: Sentry DSN for error monitoring  
**How to get it**:
1. Go to: https://sentry.io
2. Sign up (free tier available)
3. Create new project
4. Select "FastAPI" as platform
5. Copy the DSN (looks like: `https://xxx@xxx.ingest.sentry.io/xxx`)
6. Paste as: `SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx`

**Note**: Optional - app works without it

---

## 📝 ALREADY SET (No Action Needed)

These have default values and usually don't need changing:

- `APP_NAME=Patent Alert API` ✅
- `APP_VERSION=1.0.0` ✅
- `DEBUG=True` (set to `False` in production)
- `ENVIRONMENT=development` (set to `production` when deploying)
- `DATABASE_URL=sqlite:///./patent_alert.db` ✅ (SQLite for dev)
- `REDIS_CACHE_TTL=86400` ✅
- `USPTO_PATENTSVIEW_URL` ✅ (already set)
- `USPTO_BULK_DATA_URL` ✅ (already set)
- `HF_MODEL_NAME=facebook/bart-large-cnn` ✅
- `JWT_ALGORITHM=HS256` ✅
- `JWT_EXPIRATION_HOURS=24` ✅
- `API_RATE_LIMIT_PER_MINUTE=60` ✅
- `API_RATE_LIMIT_PER_DAY=10000` ✅
- `DEFAULT_BRANDING=True` ✅
- `WEBHOOK_RETRY_ATTEMPTS=3` ✅
- `WEBHOOK_RETRY_DELAY=5` ✅
- `WEBHOOK_TIMEOUT=30` ✅
- `ADMIN_USERNAME=admin` ✅
- `ALLOWED_ORIGINS` ✅ (update for production)
- `SMTP_SERVER=smtp.gmail.com` ✅
- `SMTP_PORT=587` ✅
- `ENABLE_METRICS=True` ✅

---

## 🚀 Quick Start Minimum

**To get started immediately, you only need 3 things:**

1. ✅ `SECRET_KEY` - Generate with Python command above
2. ✅ `USPTO_API_KEY` - Get from developer.uspto.gov
3. ✅ `ADMIN_PASSWORD` - Create your own strong password

Everything else is optional and can be added later!

---

## 📋 Checklist

Copy this and check off as you go:

- [ ] Generated `SECRET_KEY` (Python command)
- [ ] Got `USPTO_API_KEY` (developer.uspto.gov)
- [ ] Set `ADMIN_PASSWORD` (your own password)
- [ ] Setup Redis (Upstash or local) - Optional
- [ ] Setup Stripe keys - Optional (for billing)
- [ ] Setup Gmail SMTP - Optional (for emails)
- [ ] Setup Hugging Face key - Optional (for AI)
- [ ] Setup Sentry - Optional (for error tracking)

---

## 💡 Pro Tips

1. **Start Simple**: Get the 3 required keys first, test the API, then add optional features
2. **Test Mode First**: Use Stripe test keys (`sk_test_`) before going live
3. **Free Tiers**: All services above have free tiers sufficient for MVP
4. **Security**: Never commit `.env` to Git (it's already in `.gitignore`)

---

## 🆘 Need Help?

If you get stuck getting any key:
- Check the service's documentation
- Most services have "Getting Started" guides
- Free tiers are usually sufficient for development

