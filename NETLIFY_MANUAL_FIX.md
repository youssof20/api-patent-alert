# 🔧 Netlify Manual Fix (Required)

Netlify is still auto-detecting Python. You need to manually configure it in the dashboard.

## Quick Fix Steps

### 1. Go to Netlify Dashboard
- Open your site in Netlify
- Click **Site settings** (gear icon)

### 2. Build & Deploy Settings
- Click **Build & deploy** in left sidebar
- Scroll to **Build settings**

### 3. Override Auto-Detection
Click **Edit settings** and set:

- **Base directory**: (leave empty)
- **Build command**: `echo "Static site"`
- **Publish directory**: `landing`
- **Python version**: (leave empty or set to "None")

### 4. Environment Variables
- Go to **Environment variables**
- Make sure there are NO Python-related variables
- If you see `PYTHON_VERSION`, delete it

### 5. Deploy
- Go to **Deploys** tab
- Click **Trigger deploy** → **Deploy site**
- It should work now!

## Alternative: Create Separate Repo

If this still doesn't work, create a separate repo just for the landing page:

1. **Create new repo**: `patent-alert-landing`
2. **Copy files**:
   ```bash
   mkdir patent-alert-landing
   cp landing/index.html patent-alert-landing/
   ```
3. **Deploy to Netlify**:
   - Connect the new repo
   - Netlify will auto-detect it as static HTML
   - No Python detection issues

## Why This Happens

Netlify sees `requirements.txt` and auto-detects Python. Even with `netlify.toml`, sometimes you need to manually override in the dashboard.

## Verify It Works

After deploying:
- ✅ No Python/Rust errors
- ✅ Landing page loads
- ✅ All links work

---

**Quickest Solution**: Update the dashboard settings as shown above (2 minutes).

