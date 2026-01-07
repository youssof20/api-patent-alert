# 🔴 Upstash Redis Setup Guide

## You Got REST API Credentials, But We Need Redis Protocol URL

Upstash provides **two types of connections**:
1. **REST API** (what you got) - Uses HTTP requests
2. **Redis Protocol** (what we need) - Uses `redis://` URL

## ✅ How to Get the Redis Protocol URL

### Step 1: Go to Your Upstash Dashboard
1. Go to: https://console.upstash.com
2. Login to your account
3. Click on your Redis database (the one you just created)

### Step 2: Find the Redis URL
In your database dashboard, look for one of these sections:
- **"Redis URL"** or **"Connection String"**
- **"Details"** tab
- **"Connect"** button

You should see something like:
```
redis://default:YOUR_PASSWORD@YOUR_ENDPOINT.upstash.io:6379
```

### Step 3: Copy the Full URL
The format should be:
```
redis://default:PASSWORD@ENDPOINT.upstash.io:6379
```

### Step 4: Add to Your .env
```env
REDIS_URL=redis://default:YOUR_PASSWORD@YOUR_ENDPOINT.upstash.io:6379
```

---

## 🔍 If You Can't Find the Redis URL

### Option A: Check the "Details" Tab
1. In your database dashboard
2. Click "Details" tab
3. Look for "Redis URL" or "Connection String"

### Option B: Check the "Connect" Section
1. Look for a "Connect" or "Connection" button
2. It might show different connection methods
3. Select "Redis" (not "REST API")

### Option C: It Might Be in the REST Token Section
Sometimes Upstash shows both in the same place. Look for:
- **REST URL**: `https://...` (what you have)
- **Redis URL**: `redis://...` (what you need)

---

## 📝 Example Format

Your Redis URL should look like this:
```
redis://default:AXAAACQgYjE4YjY3YjYtYjY3YjY3YjY3YjY3YjY3YjY3YjY3YjY3@capital-lion-26807.upstash.io:6379
```

Notice:
- Starts with `redis://` (not `https://`)
- Has `default:` username
- Has a password (long string)
- Has `@` symbol
- Has your endpoint: `capital-lion-26807.upstash.io`
- Has port: `:6379`

---

## ⚠️ If You Only See REST API

If Upstash only shows REST API credentials, you have two options:

### Option 1: Use Local Redis (Development)
```env
REDIS_URL=redis://localhost:6379/0
```
Then install Redis locally or use Docker:
```bash
docker run -d -p 6379:6379 redis
```

### Option 2: Use Another Redis Service
- **Redis Cloud**: https://redis.com/cloud (free tier)
- **Railway**: https://railway.app (has Redis)
- **Render**: https://render.com (has Redis addon)

---

## ✅ Quick Test

Once you have the Redis URL in your `.env`, test it:

```bash
python -c "from app.services.cache_service import CacheService; cs = CacheService(); print('Redis connected!' if cs.redis_client else 'Redis not connected')"
```

If it says "Redis connected!", you're good! ✅

---

## 🆘 Still Can't Find It?

1. **Check Upstash Documentation**: https://docs.upstash.com/redis
2. **Contact Upstash Support**: They're very helpful
3. **Use Local Redis**: For development, local Redis works fine

---

## 💡 Pro Tip

The REST API credentials you got can be used for other purposes (like serverless functions), but for our Python app, we need the Redis protocol URL.

