# 📋 Quick Reference - Post Deployment

## 🔗 Your API URLs

- **API Base**: https://api-patent-alert.onrender.com
- **Documentation**: https://api-patent-alert.onrender.com/docs
- **Health Check**: https://api-patent-alert.onrender.com/health
- **Stripe Webhook**: https://api-patent-alert.onrender.com/api/v1/billing/webhook

## ✅ Quick Test Checklist

- [ ] Health endpoint returns 200
- [ ] Docs page loads
- [ ] Can create API key
- [ ] Can query patents with API key
- [ ] Usage stats work
- [ ] Admin dashboard accessible

## 🔑 Environment Variables (Render)

**Required:**
- `SECRET_KEY`
- `USPTO_API_KEY`
- `ADMIN_PASSWORD`

**Recommended:**
- `REDIS_URL`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

## 📞 Support

- Email: youssoufsallam25@gmail.com
- Docs: `/docs` endpoint
- Logs: Render Dashboard → Logs

## 🚀 Next Actions

1. Test API endpoints
2. Set up Stripe webhook
3. Start customer outreach
4. Monitor usage and errors

See `POST_DEPLOYMENT_STEPS.md` for detailed guide.

