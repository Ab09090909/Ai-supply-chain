import streamlit as st
from utils.db_helpers import update_user

def render_profile(user_info):
    """Render the business card profile"""
    
    # CSS for profile
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
    .card-container {
        display: flex;
        align-items: center;
        gap: 25px;
    }
    .card-left {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 200px;
        border-right: 2px solid #1e293b;
        padding-right: 25px;
    }
    .profile-pic-large {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
        font-weight: bold;
        color: white;
        border: 4px solid #fff;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        margin-bottom: 15px;
    }
    .card-name {
        font-size: 22px;
        font-weight: bold;
        color: #1e293b;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0;
        text-align: center;
    }
    .card-title {
        font-size: 13px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 5px 0 0 0;
        text-align: center;
    }
    .card-right {
        flex: 1;
    }
    .contact-item {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
        font-size: 14px;
        color: #1e293b;
        flex-wrap: wrap;
    }
    .contact-icon {
        font-size: 18px;
        width: 24px;
        text-align: center;
        flex-shrink: 0;
    }
    .contact-label {
        font-weight: 600;
        color: #475569;
        min-width: 80px;
    }
    .contact-value {
        color: #1e293b;
        font-weight: 500;
        word-break: break-word;
        flex: 1;
    }
    .edit-profile-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s;
        margin-top: 15px;
        width: 100%;
    }
    .edit-profile-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    @media screen and (max-width: 768px) {
        .business-card {
            padding: 20px 15px;
            margin: 0 10px 20px 10px;
        }
        .card-container {
            flex-direction: column;
            gap: 20px;
        }
        .card-left {
            border-right: none;
            border-bottom: 2px solid #1e293b;
            padding-right: 0;
            padding-bottom: 20px;
            width: 100%;
        }
        .profile-pic-large {
            width: 100px;
            height: 100px;
            font-size: 40px;
        }
        .card-name {
            font-size: 20px;
        }
        .card-right {
            width: 100%;
        }
        .contact-item {
            font-size: 13px;
            margin-bottom: 10px;
        }
        .contact-label {
            min-width: 70px;
            font-size: 13px;
        }
        .contact-value {
            font-size: 13px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get user data
    name = user_info.get('name', 'Not specified')
    initial = name[0].upper() if name else "P"
    email = user_info.get('email', 'Not specified')
    phone = user_info.get('phone', 'Not specified')
    company = user_info.get('company_name', 'Not specified')
    address = user_info.get('address', 'Not specified')
    region = user_info.get('region', 'Addis Ababa')
    
    # Render Business Card
    st.markdown(f"""
    <div class="business-card">
        <div class="card-container">
            <div class="card-left">
                <div class="profile-pic-large">{initial}</div>
                <p class="card-name">{name}</p>
                <p class="card-title">Producer • {company}</p>
            </div>
            <div class="card-right">
                <div class="contact-item">
                    <span class="contact-icon">🏠</span>
                    <span class="contact-label">Address:</span>
                    <span class="contact-value">{address}, {region}</span>
                </div>
                <div class="contact-item">
                    <span class="contact-icon">📞</span>
                    <span class="contact-label">Phone:</span>
                    <span class="contact-value">{phone}</span>
                </div>
                <div class="contact-item">
                    <span class="contact-icon">✉️</span>
                    <span class="contact-label">Email:</span>
                    <span class="contact-value">{email}</span>
                </div>
                <div class="contact-item">
                    <span class="contact-icon">🏢</span>
                    <span class="contact-label">Company:</span>
                    <span class="contact-value">{company}</span>
                </div>
                <div class="contact-item">
                    <span class="contact-icon">🌍</span>
                    <span class="contact-label">Region:</span>
                    <span class="contact-value">{region}</span>
                </div>
                <button class="edit-profile-btn" onclick="document.getElementById('edit-profile-section').scrollIntoView({{behavior: 'smooth'}})">✏️ Edit Profile</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_edit_profile(user_info):
    """Render the edit profile section"""
    st.markdown('<div id="edit-profile-section"></div>', unsafe_allow_html=True)
    
    with st.expander("✏️ Edit Profile Information", expanded=st.session_state.get('show_edit_profile', False)):
        st.markdown("### Update Your Business Card Information")
        
        with st.form("edit_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("Full Name", value=user_info.get('name', ''))
                new_email = st.text_input("Email", value=user_info.get('email', ''))
                new_phone = st.text_input("Phone Number", value=user_info.get('phone', ''))
            
            with col2:
                new_company = st.text_input("Company Name", value=user_info.get('company_name', ''))
                new_address = st.text_input("Address", value=user_info.get('address', ''))
                regions = ["Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNP", "Sidama", 
                          "Afar", "Benishangul-Gumuz", "Gambella", "Harari", "Dire Dawa", "Somali"]
                current_region = user_info.get('region', 'Addis Ababa')
                region_idx = regions.index(current_region) if current_region in regions else 0
                new_region = st.selectbox("Region", regions, index=region_idx)
            
            col1, col2 = st.columns(2)
            with col1:
                save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
            with col2:
                cancel_btn = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if save_btn:
                if new_name and new_email:
                    try:
                        update_user(user_info['id'], 
                                   name=new_name, 
                                   email=new_email,
                                   phone=new_phone,
                                   company_name=new_company,
                                   address=new_address,
                                   region=new_region)
                        
                        st.session_state.user_info['name'] = new_name
                        st.session_state.user_info['email'] = new_email
                        st.session_state.user_info['phone'] = new_phone
                        st.session_state.user_info['company_name'] = new_company
                        st.session_state.user_info['address'] = new_address
                        st.session_state.user_info['region'] = new_region
                        
                        st.success("✅ Profile updated successfully!")
                        st.session_state.show_edit_profile = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating profile: {e}")
                else:
                    st.error("Name and Email are required!")
            
            if cancel_btn:
                st.session_state.show_edit_profile = False
                st.rerun()
