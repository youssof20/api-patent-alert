"""
Streamlit admin dashboard
"""
import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.user import APIKey
from app.models.usage import APIUsage
from app.utils.helpers import generate_api_key
import stripe
from app.config import settings

# Configure Streamlit page
st.set_page_config(
    page_title="Patent Alert API - Admin Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize Stripe if configured
if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let Streamlit handle it


def main():
    """Main dashboard function"""
    # Check authentication
    from app.admin.auth import check_admin_password, logout
    check_admin_password()
    
    st.title("📊 Patent Alert API - Admin Dashboard")
    
    # Logout button
    if st.sidebar.button("Logout"):
        logout()
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Overview", "Partners", "Usage Analytics", "Billing", "Settings"]
    )
    
    if page == "Overview":
        show_overview()
    elif page == "Partners":
        show_partners()
    elif page == "Usage Analytics":
        show_analytics()
    elif page == "Billing":
        show_billing()
    elif page == "Settings":
        show_settings()


def show_overview():
    """Show overview dashboard"""
    st.header("Overview")
    
    db = get_db()
    
    try:
        # Total partners
        total_partners = db.query(func.count(APIKey.id)).filter(
            APIKey.is_active == True
        ).scalar() or 0
        
        # Total queries (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        total_queries = db.query(func.count(APIUsage.id)).filter(
            APIUsage.created_at >= thirty_days_ago
        ).scalar() or 0
        
        # Total revenue (last 30 days)
        total_revenue = db.query(func.sum(APIUsage.cost)).filter(
            APIUsage.created_at >= thirty_days_ago
        ).scalar() or 0.0
        
        # Active API keys
        active_keys = db.query(APIKey).filter(
            APIKey.is_active == True
        ).count()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Partners", total_partners)
        
        with col2:
            st.metric("Total Queries (30d)", f"{total_queries:,}")
        
        with col3:
            st.metric("Revenue (30d)", f"${total_revenue:,.2f}")
        
        with col4:
            st.metric("Active API Keys", active_keys)
        
        # Recent activity
        st.subheader("Recent Activity")
        recent_usage = db.query(APIUsage).order_by(
            APIUsage.created_at.desc()
        ).limit(10).all()
        
        if recent_usage:
            usage_data = []
            for usage in recent_usage:
                usage_data.append({
                    "Timestamp": usage.created_at,
                    "Partner": usage.api_key.partner_name,
                    "Endpoint": usage.endpoint,
                    "Status": usage.response_status,
                    "Response Time (ms)": f"{usage.response_time_ms:.2f}" if usage.response_time_ms else "N/A",
                    "Cost": f"${usage.cost:.2f}" if usage.cost else "N/A"
                })
            
            df = pd.DataFrame(usage_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No recent activity")
            
    finally:
        db.close()


def show_partners():
    """Show partners management"""
    st.header("Partners Management")
    
    db = get_db()
    
    try:
        # Create new partner
        with st.expander("Create New Partner"):
            partner_name = st.text_input("Partner Name")
            partner_email = st.text_input("Partner Email")
            rate_limit_min = st.number_input("Rate Limit (per minute)", min_value=1, value=60)
            rate_limit_day = st.number_input("Rate Limit (per day)", min_value=1, value=10000)
            branding = st.checkbox("Enable Branding", value=True)
            
            if st.button("Create API Key"):
                if partner_name and partner_email:
                    new_key = generate_api_key()
                    api_key = APIKey(
                        key=new_key,
                        partner_name=partner_name,
                        partner_email=partner_email,
                        rate_limit_per_minute=rate_limit_min,
                        rate_limit_per_day=rate_limit_day,
                        branding_enabled=branding
                    )
                    db.add(api_key)
                    db.commit()
                    st.success(f"API Key created: `{new_key}`")
                    st.info("⚠️ Save this key securely - it won't be shown again!")
                else:
                    st.error("Please fill in all required fields")
        
        # List partners
        st.subheader("Active Partners")
        partners = db.query(APIKey).filter(APIKey.is_active == True).all()
        
        if partners:
            partner_data = []
            for partner in partners:
                # Get usage stats
                usage_count = db.query(func.count(APIUsage.id)).filter(
                    APIUsage.api_key_id == partner.id,
                    APIUsage.created_at >= datetime.utcnow() - timedelta(days=30)
                ).scalar() or 0
                
                partner_data.append({
                    "ID": partner.id,
                    "Partner Name": partner.partner_name,
                    "Email": partner.partner_email,
                    "Queries (30d)": usage_count,
                    "Created": partner.created_at.strftime("%Y-%m-%d"),
                    "Status": "Active" if partner.is_active else "Inactive"
                })
            
            df = pd.DataFrame(partner_data)
            st.dataframe(df, use_container_width=True)
            
            # Revoke option
            st.subheader("Revoke API Key")
            partner_ids = [p.id for p in partners]
            selected_id = st.selectbox("Select Partner", partner_ids, format_func=lambda x: next(p.partner_name for p in partners if p.id == x))
            
            if st.button("Revoke API Key", type="primary"):
                partner = db.query(APIKey).filter(APIKey.id == selected_id).first()
                if partner:
                    partner.is_active = False
                    db.commit()
                    st.success("API Key revoked successfully")
                    st.rerun()
        else:
            st.info("No active partners")
            
    finally:
        db.close()


def show_analytics():
    """Show usage analytics"""
    st.header("Usage Analytics")
    
    db = get_db()
    
    try:
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.utcnow().date() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", value=datetime.utcnow().date())
        
        # Query usage data
        usage_data = db.query(APIUsage).filter(
            func.date(APIUsage.created_at) >= start_date,
            func.date(APIUsage.created_at) <= end_date
        ).all()
        
        if usage_data:
            # Daily usage chart
            daily_counts = {}
            for usage in usage_data:
                date = usage.created_at.date()
                daily_counts[date] = daily_counts.get(date, 0) + 1
            
            chart_data = pd.DataFrame({
                "Date": list(daily_counts.keys()),
                "Queries": list(daily_counts.values())
            }).sort_values("Date")
            
            st.subheader("Daily Query Volume")
            st.line_chart(chart_data.set_index("Date"))
            
            # Endpoint breakdown
            endpoint_counts = {}
            for usage in usage_data:
                endpoint_counts[usage.endpoint] = endpoint_counts.get(usage.endpoint, 0) + 1
            
            st.subheader("Endpoint Usage")
            endpoint_df = pd.DataFrame({
                "Endpoint": list(endpoint_counts.keys()),
                "Count": list(endpoint_counts.values())
            }).sort_values("Count", ascending=False)
            st.bar_chart(endpoint_df.set_index("Endpoint"))
            
            # Response time distribution
            response_times = [u.response_time_ms for u in usage_data if u.response_time_ms]
            if response_times:
                st.subheader("Response Time Distribution")
                st.metric("Average", f"{sum(response_times) / len(response_times):.2f} ms")
                st.metric("Min", f"{min(response_times):.2f} ms")
                st.metric("Max", f"{max(response_times):.2f} ms")
        else:
            st.info("No usage data for selected period")
            
    finally:
        db.close()


def show_billing():
    """Show billing information"""
    st.header("Billing & Revenue")
    
    db = get_db()
    
    try:
        # Revenue metrics
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        total_revenue = db.query(func.sum(APIUsage.cost)).filter(
            APIUsage.created_at >= thirty_days_ago
        ).scalar() or 0.0
        
        st.metric("Revenue (Last 30 Days)", f"${total_revenue:,.2f}")
        
        # Revenue by partner
        st.subheader("Revenue by Partner")
        partner_revenue = db.query(
            APIKey.partner_name,
            func.sum(APIUsage.cost).label("revenue")
        ).join(
            APIUsage, APIKey.id == APIUsage.api_key_id
        ).filter(
            APIUsage.created_at >= thirty_days_ago
        ).group_by(APIKey.partner_name).all()
        
        if partner_revenue:
            revenue_df = pd.DataFrame(partner_revenue, columns=["Partner", "Revenue"])
            revenue_df = revenue_df.sort_values("Revenue", ascending=False)
            st.dataframe(revenue_df, use_container_width=True)
            
            # Chart
            st.bar_chart(revenue_df.set_index("Partner"))
        else:
            st.info("No revenue data")
        
        # Stripe integration status
        st.subheader("Stripe Integration")
        if settings.stripe_secret_key:
            st.success("✅ Stripe configured")
            # Add Stripe dashboard link or webhook management here
        else:
            st.warning("⚠️ Stripe not configured. Add STRIPE_SECRET_KEY to .env")
            
    finally:
        db.close()


def show_settings():
    """Show settings"""
    st.header("Settings")
    
    st.subheader("Application Configuration")
    st.json({
        "App Name": settings.app_name,
        "Version": settings.app_version,
        "Environment": settings.environment,
        "Debug": settings.debug
    })
    
    st.subheader("API Configuration")
    st.json({
        "Rate Limit (per minute)": settings.api_rate_limit_per_minute,
        "Rate Limit (per day)": settings.api_rate_limit_per_day,
        "Default Branding": settings.default_branding
    })
    
    st.subheader("External Services")
    services_status = {
        "USPTO API": "✅ Configured" if settings.uspto_api_key else "❌ Not configured",
        "Hugging Face": "✅ Configured" if settings.hf_api_key else "❌ Not configured",
        "Redis": "✅ Configured" if settings.redis_url else "❌ Not configured",
        "Stripe": "✅ Configured" if settings.stripe_secret_key else "❌ Not configured"
    }
    st.json(services_status)


if __name__ == "__main__":
    main()

