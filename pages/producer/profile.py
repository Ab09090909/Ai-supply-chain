import streamlit as st
from utils.db_helpers import update_user

def render_profile(user_info):
    """Render producer profile card and edit form"""
    
    # CSS for profile card
    st.markdown("""
    <style>
    .business-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        border: 1px solid #e2e8f0;
        max-width: 800px;
        margin: 0 auto 20px auto;
    }
    .card-container { display: flex; align-items: center; gap: 25px; }
    .card-left {
        display: flex; flex-direction: column; align-items: center;
        min-width: 200px; border-right: 2px solid #1e293b; padding-right: 25px;
    }
    .profile-pic-large {
        width: 100px; height: 100px; border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 40px; font-weight: bold; color: white;
        border: 4px solid #fff; margin-bottom: 15px;
    }
    .card-name { font-size: 20px; font-weight: bold; color: #1e293b; margin: 0; text-align: center; }
    .card-title { font-size: 13px; color: #64748b; margin: 5px 0 0 0; text-align: center; }
    .card-right { flex: 1; }
    .contact-item { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; font-size: 14px; color: #1e293b; }
    .contact-icon { font-size: 18px; width: 24px; text-align: center; }
    .contact-label { font-weight: 600; color: #475569; min-width: 80px; }
    .edit-profile-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; padding: 10px 20px; border-radius: 8px;
        cursor: pointer; font-weight: 600; margin-top: 15px; width: 100%;
    }
    @media screen and (max-width: 768px) {
        .card-container { flex-direction: column; }
        .card-left { border-right: none; border-bottom: 2px solid #1e293b; padding-bottom: 20px; width: 100%; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Profile card
    name = user_info.get('name', 'Not specified')
    initial = name[0].upper() if name else "P"
    
    st.markdown(f"""
    <div class="business-card">
        <div class="card-container">
            <div class="card-left">
                <div class="profile-pic-large">{initial}</div>
                <p class="card-name">{name}</p>
                <p class="card-title">Producer • {user_info.get('company_name', 'Independent')}</p>
            </div>
            <div class="card-right">
                <div class="contact-item"><span class="contact-icon">📧</span><span class="contact-label">Email:</span><span>{user_info.get('email', '')}</span></div>
                <div class="contact-item"><span class="contact-icon">📞</span><span class="contact-label">Phone:</span><span>{user_info.get('phone', 'N/A')}</span></div>
                <div class="contact-item"><span class="contact-icon">🌍</span><span class="contact-label">Region:</span><span>{user_info.get('region', 'Addis Ababa')}</span></div>
                <button class="edit-profile-btn" onclick="document.getElementById('edit-profile-section').scrollIntoView({{behavior: 'smooth'}})">✏️ Edit Profile</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Edit profile form
    st.markdown('<div id="edit-profile-section"></div>', unsafe_allow_html=True)
    with st.expander("✏️ Edit Profile Information", expanded=False):
        with st.form("edit_profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Full Name", value=user_info.get('name', ''))
                new_phone = st.text_input("Phone Number", value=user_info.get('phone', ''))
            with col2:
                new_company = st.text_input("Company Name", value=user_info.get('company_name', ''))
                regions = ["Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNP", "Sidama", "Afar", "Benishangul-Gumuz", "Gambella", "Harari", "Dire Dawa", "Somali"]
                new_region = st.selectbox("Region", regions, index=regions.index(user_info.get('region', 'Addis Ababa')) if user_info.get('region') in regions else 0)
            
            if st.form_submit_button("💾 Save Changes", type="primary"):
                update_user(user_info['id'], name=new_name, phone=new_phone, company_name=new_company, region=new_region)
                st.session_state.user_info.update({'name': new_name, 'phone': new_phone, 'company_name': new_company, 'region': new_region})
                st.success("✅ Profile updated!")
                st.rerun()
