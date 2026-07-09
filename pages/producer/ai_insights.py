import streamlit as st
from utils.db_helpers import get_products

REGIONS = [
    'Addis Ababa', 'Oromia', 'Amhara', 'Tigray',
    'SNNPR', 'Somali', 'Afar', 'Dire Dawa', 'Harari', 'Benishangul-Gumuz'
]

def render_ai_insights(user_info, ai):
    st.subheader("🤖 AI Market Insights")
    products = get_products(producer_id=user_info.get('id'))
    names = [p['name'] for p in products] if products else []

    col1, col2 = st.columns(2)
    with col1:
        sel_product = st.selectbox(
            "Product",
            names if names else ["No products yet"],
            key="ai_selected_product"
        )
    with col2:
        sel_region = st.selectbox("Region", REGIONS, key="ai_selected_region")

    if st.button("🔍 Get AI Insights", use_container_width=True):
        if not names:
            st.warning("⚠️ Add products first.")
            return
        with st.spinner("Analyzing..."):
            st.markdown("### 💰 Price Recommendation")
            ranges = getattr(ai, 'ethiopian_price_ranges', {})
            if sel_product in ranges:
                r = ranges[sel_product]
                st.info(f"Recommended: **{r['avg']} ETB/{r['unit']}** (Range: {r['min']}–{r['max']})")
            else:
                st.info(f"No price data for {sel_product}. Check local market rates.")

            st.markdown("### 📈 Demand Forecast")
            st.info(
                f"Demand for **{sel_product}** in {sel_region} is typically high during "
                "harvest season. Consider stocking 10–20% more during peak months."
            )

            st.markdown("### 💡 Market Tips")
            tip = (
                ai.get_market_tip() if hasattr(ai, 'get_market_tip')
                else f"Keep your **{sel_product}** listing updated with accurate stock levels."
            )
            st.success(tip)
