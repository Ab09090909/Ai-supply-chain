import streamlit as st
import pandas as pd
from utils.db_helpers import get_orders

STATUS_ICONS = {
    'pending': '🟡', 'confirmed': '🔵',
    'shipped': '🟠', 'delivered': '🟢', 'cancelled': '🔴',
}


def render_orders(user_info):
    st.subheader("🚚 Orders")
    user_id = user_info.get('id')
    orders = get_orders(user_id=user_id, role='producer')

    if not orders:
        st.info("📭 No orders yet.")
        return

    df = pd.DataFrame(orders)
    statuses = ['All'] + sorted(df['status'].unique().tolist()) if 'status' in df.columns else ['All']
    selected = st.selectbox("Filter by status", statuses)

    if selected != 'All' and 'status' in df.columns:
        df = df[df['status'] == selected]

    if 'status' in df.columns:
        df['status'] = df['status'].apply(lambda s: f"{STATUS_ICONS.get(s, '⚪')} {s.capitalize()}")

    cols = [c for c in ['id', 'status', 'total_amount', 'created_at'] if c in df.columns]
    st.dataframe(df[cols], use_container_width=True)
    st.caption(f"Showing {len(df)} order(s)")
