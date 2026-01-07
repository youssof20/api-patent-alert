# 🚀 Deploy Landing Page Guide

## Quick Deploy Options

### Option 1: Netlify (Easiest - 5 minutes)

1. **Go to**: https://netlify.com
2. **Sign up** (free)
3. **Drag & Drop**:
   - Drag the `landing` folder to Netlify
   - Or: New site → Deploy manually → Upload `landing` folder
4. **Done!** Your site is live at `your-site.netlify.app`

**Custom Domain** (Optional):
- Add domain in Netlify settings
- Update DNS records
- Cost: $0 (free tier)

### Option 2: Vercel (Also Easy)

1. **Go to**: https://vercel.com
2. **Sign up** (free)
3. **Import Git Repository**:
   - Create new repo with `landing/index.html`
   - Push to GitHub
   - Import in Vercel
4. **Deploy!** Live at `your-site.vercel.app`

### Option 3: GitHub Pages (Free)

1. **Create GitHub Repo**: `patent-alert-landing`
2. **Upload Files**: Add `landing/index.html`
3. **Settings → Pages**:
   - Source: `main` branch
   - Folder: `/` (root)
4. **Live at**: `your-username.github.io/patent-alert-landing`

### Option 4: Render (Same as API)

1. **Render Dashboard** → New → Static Site
2. **Connect GitHub** repo with landing page
3. **Build Command**: (none needed - static HTML)
4. **Publish Directory**: `landing`
5. **Deploy!**

## Update Links After Deploy

Once deployed, update these in `landing/index.html`:

1. **API Docs Link**: 
   - Find: `https://api-patent-alert.onrender.com/docs`
   - Verify it's correct

2. **Email Links**:
   - Find: `betterappsstudio@gmail.com`
   - Verify it's correct

3. **Custom Domain** (if you have one):
   - Update all `api-patent-alert.onrender.com` references
   - Or keep as-is (works fine)

## SEO Optimization (Optional)

Add to `<head>` section if you want better Google ranking:

```html
<!-- Google Analytics (Optional) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

Get GA ID from: https://analytics.google.com

## Test Before Going Live

- [ ] All links work
- [ ] Mobile responsive (test on phone)
- [ ] CTA buttons work
- [ ] Email links open correctly
- [ ] API docs link works
- [ ] Pricing is correct

## Done!

Your landing page is live. Share it in:
- Outreach emails
- LinkedIn posts
- Product Hunt launch
- Social media

**Next**: Start customer outreach using `SALES_MATERIALS.md`!

