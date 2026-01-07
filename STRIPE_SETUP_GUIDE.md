# 💳 Stripe Pricing Setup Guide

## Overview

This guide walks you through setting up Stripe products and pricing for your Patent Alert API tiers.

## Pricing Tiers

- **Starter**: $499/month - 10,000 queries/month
- **Professional**: $1,999/month - Unlimited queries
- **Enterprise**: Custom pricing (contact sales)

## Step-by-Step Stripe Setup

### Step 1: Create Products in Stripe Dashboard

1. **Go to Stripe Dashboard**: https://dashboard.stripe.com
2. **Navigate to**: Products → Add Product

#### Create Starter Plan

- **Name**: `Patent Alert API - Starter`
- **Description**: `Up to 10,000 queries/month with basic AI filtering`
- **Pricing Model**: Standard pricing
- **Price**: `$499.00`
- **Billing Period**: Monthly (recurring)
- **Currency**: USD
- **Trial Period**: 14 days (optional - can be set in code)
- Click **Save Product**

**Copy the Price ID** (starts with `price_`) - you'll need this!

#### Create Professional Plan

- **Name**: `Patent Alert API - Professional`
- **Description**: `Unlimited queries with advanced AI and priority support`
- **Pricing Model**: Standard pricing
- **Price**: `$1,999.00`
- **Billing Period**: Monthly (recurring)
- **Currency**: USD
- **Trial Period**: 14 days
- Click **Save Product**

**Copy the Price ID** (starts with `price_`)

### Step 2: Configure Free Trial

**Option A: Set in Stripe Dashboard** (Recommended)
- In each product, go to "Pricing"
- Enable "Add a trial period"
- Set to 14 days
- Save

**Option B: Set in Code** (More flexible)
- Already implemented in `app/api/routes/stripe.py`
- Trial is set when creating checkout session

### Step 3: Set Up Usage-Based Billing (Optional)

For overage charges ($0.05 per query over limit):

1. **Create Metered Price**:
   - Products → Add Product
   - Name: `Patent Alert API - Overage`
   - Pricing: Metered pricing
   - Unit Amount: `$0.05` per query
   - Billing: Per unit
   - Save

2. **Track Usage in Your API**:
   - Already implemented in `app/models/usage.py`
   - Track query counts per API key
   - Report to Stripe using Usage Records API

### Step 4: Update Environment Variables

Add to Render (or your `.env`):

```env
STRIPE_SECRET_KEY=sk_live_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

**Get these from**: Stripe Dashboard → Developers → API keys

### Step 5: Set Up Webhook Endpoint

1. **Stripe Dashboard** → Developers → Webhooks
2. **Add Endpoint**:
   - URL: `https://api-patent-alert.onrender.com/api/v1/billing/webhook`
   - Description: `Patent Alert API Webhooks`
3. **Select Events**:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.trial_will_end`
4. **Copy Signing Secret**: Starts with `whsec_`
5. **Add to Environment**: `STRIPE_WEBHOOK_SECRET=whsec_...`

### Step 6: Test in Test Mode First

**Important**: Test everything in Stripe test mode before going live!

1. **Use Test Keys**:
   - `sk_test_...` (secret key)
   - `pk_test_...` (publishable key)

2. **Test Checkout Flow**:
   - Create test checkout session
   - Use test card: `4242 4242 4242 4242`
   - Complete checkout
   - Verify webhook received

3. **Test Webhooks Locally** (Optional):
   - Use Stripe CLI: `stripe listen --forward-to localhost:8000/api/v1/billing/webhook`
   - Test events in dashboard

### Step 7: Update Code with Price IDs (Optional)

If you want to use Stripe Price IDs directly instead of hardcoded prices:

1. **Add to Environment Variables**:
   ```env
   STRIPE_STARTER_PRICE_ID=price_xxxxx
   STRIPE_PROFESSIONAL_PRICE_ID=price_xxxxx
   ```

2. **Update `app/api/routes/stripe.py`**:
   ```python
   # Use price IDs from environment
   price_id = os.getenv(f"STRIPE_{plan.upper()}_PRICE_ID")
   if price_id:
       checkout_session = stripe.checkout.Session.create(
           line_items=[{'price': price_id, 'quantity': 1}],
           ...
       )
   ```

**Note**: Current implementation uses hardcoded prices which is simpler and works fine.

## Pricing Strategy Rationale

### Why $499 Starter?
- **Market Research**: Similar IP APIs (Clarivate, PatSnap) charge $1K+/month
- **Value Proposition**: 50-80% time savings worth $10K+/year to firms
- **Conversion**: Lower barrier than $1K+ but still premium positioning
- **Margins**: 80-90% margins at scale (low infrastructure costs)

### Why $1,999 Professional?
- **Target**: Mid-market legal tech companies ($50K-500K ARR)
- **Unlimited Queries**: Removes friction for high-volume users
- **Premium Positioning**: 4x Starter shows clear value tier
- **LTV**: $24K/year per customer = strong unit economics

### Why 14-Day Free Trial?
- **Conversion Data**: 2-3x better conversion vs. paid trials (Stripe benchmarks)
- **Low Friction**: No credit card = more signups
- **Trust Building**: Time to integrate and see value
- **B2B Standard**: Industry norm for API products

## Monitoring & Analytics

### Track in Stripe Dashboard:
- **MRR**: Monthly Recurring Revenue
- **Churn**: Subscription cancellations
- **Trial Conversion**: Free → Paid rate
- **Average Revenue Per User (ARPU)**

### Track in Your Admin Dashboard:
- API usage per customer
- Query costs
- Customer health scores

## Common Issues & Solutions

### Issue: Webhook Not Receiving Events
**Solution**: 
- Verify webhook URL is correct
- Check `STRIPE_WEBHOOK_SECRET` is set
- Test with Stripe CLI locally first

### Issue: Trial Not Working
**Solution**:
- Check trial period is set in product or code
- Verify `trial_period_days=14` in checkout session

### Issue: Price Mismatch
**Solution**:
- Update `plan_prices` in `app/api/routes/stripe.py`
- Or use Stripe Price IDs from environment

## Going Live Checklist

- [ ] Test all checkout flows in test mode
- [ ] Verify webhooks work correctly
- [ ] Switch to live API keys (`sk_live_...`)
- [ ] Update webhook endpoint to production URL
- [ ] Test with real card (your own)
- [ ] Monitor first few transactions
- [ ] Set up alerts for failed payments

## Support

Questions? Contact: betterappsstudio@gmail.com

