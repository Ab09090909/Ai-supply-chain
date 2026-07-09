import streamlit as st

st.title("🔧 Debug Mode")

try:
    from producer.profile import render_profile
    st.success("✅ profile.py imported")
except Exception as e:
    st.error(f"❌ profile.py failed: {e}")

try:
    from producer.dashboard import render_dashboard
    st.success("✅ dashboard.py imported")
except Exception as e:
    st.error(f"❌ dashboard.py failed: {e}")

try:
    from producer.inventory import render_inventory
    st.success("✅ inventory.py imported")
except Exception as e:
    st.error(f"❌ inventory.py failed: {e}")

st.divider()
