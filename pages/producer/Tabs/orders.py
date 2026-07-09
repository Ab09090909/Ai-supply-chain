import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db_helpers import get_orders

def render_orders(user_info):
    """Render Orders tab"""
    st.subheader("Recent Orders")
    
    orders = get_orders(user_info['id'], 'producer', limit=50)
    
    if orders:
        df_orders = pd.DataFrame(orders)
        
        status_filter = st.selectbox("Filter by Status", ["All", "pending", "confirmed", "shipped", "delivered", "cancelled"])
        
        if status_filter != "All":
            df_orders = df_orders[df_orders['status'] == status_filter]
            
        st.dataframe(df_orders, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            fig_status = px.pie(
                df_orders, names='status', title="Order Status Distribution",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("No orders received yet.")
