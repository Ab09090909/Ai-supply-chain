# pages/producer/components/profile.py
import streamlit as st
import os
import uuid
from PIL import Image
from utils.db_helpers import update_user, update_user_profile_image

def render_profile(user_info):
    """Render the business card profile - Mobile Responsive"""
    
    # CSS for responsive business card
    st.markdown("""
    <style>
    /* Business Card Styles */
    .business-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        border: 1px solid #e2e8f0;
        max-width: 900px;
        margin: 0 auto 20px auto;
        transition: all 0.3s ease;
    }
    
    .card-container {
        display: flex;
        align-items: center;
        gap: 25px;
        flex-wrap: wrap;
    }
    
    .card-left {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 180px;
        border-right: 2px solid #1e293b;
        padding-right: 25px;
        flex-shrink: 0;
    }
    
    .profile-pic-container {
        width: 120px;
        height: 120px;
        margin-bottom: 12px;
        border-radius: 50%;
        overflow: hidden;
        border: 4px solid #fff;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    
    .profile-pic-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    
    .profile-pic-container .initial {
        font-size: 48px;
        font-weight: bold;
        color: white;
        text-align: center;
    }
    
    .card-name {
        font-size: 22px;
        font-weight: bold;
        color: #1e293b;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0;
        text-align: center;
        word-break: break-word;
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
        min-width: 200px;
    }
    
    .contact-item {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 10px;
        font-size: 14px;
        color: #1e293b;
        flex-wrap: wrap;
        padding: 4px 0;
    }
    
    .contact-icon {
        font-size: 18px;
        width: 28px;
        text-align: center;
        flex-shrink: 0;
    }
    
    .contact-label {
        font-weight: 600;
        color: #475569;
        min-width: 80px;
        font-size: 13px;
    }
    
    .contact-value {
        color: #1e293b;
        font-weight: 500;
        word-break: break-word;
        flex: 1;
        font-size: 14px;
    }
    
    .edit-profile-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        margin-top: 15px;
        width: 100%;
        max-width: 300px;
    }
    
    .edit-profile-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Responsive Styles */
    @media screen and (max-width: 768px) {
        .business-card {
            padding: 20px 15px;
            margin: 0 10px 20px 10px;
            border-radius: 12px;
        }
        
        .card-container {
            flex-direction: column;
            gap: 20px;
            align-items: stretch;
        }
        
        .card-left {
            border-right: none;
            border-bottom: 2px solid #1e293b;
            padding-right: 0;
            padding-bottom: 20px;
            width: 100%;
            min-width: unset;
        }
        
        .profile-pic-container {
            width: 100px;
            height: 100px;
        }
        
        .profile-pic-container .initial {
            font-size: 40px;
        }
        
        .card-name {
            font-size: 20px;
        }
        
        .card-right {
            width: 100%;
            min-width: unset;
        }
        
        .contact-item {
            font-size: 13px;
            padding: 6px 0;
            gap: 10px;
        }
        
        .contact-label {
            min-width: 70px;
            font-size: 12px;
        }
        
        .contact-value {
            font-size: 13px;
        }
        
        .edit-profile-btn {
            font-size: 13px;
            padding: 10px 20px;
            max-width: 100%;
        }
    }
    
    @media screen and (max-width: 480px) {
        .business-card {
            padding: 15px 12px;
            margin: 0 5px 15px 5px;
        }
        
        .profile-pic-container {
            width: 80px;
            height: 80px;
        }
        
        .profile-pic-container .initial {
            font-size: 32px;
        }
        
        .card-name {
            font-size: 18px;
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
    profile_image = user_info.get('profile_image', None)
    
    # Get role and format
    role = user_info.get('role', 'producer').capitalize()
    
    # Build profile image HTML
    profile_html = ""
    if profile_image and os.path.exists(profile_image):
        try:
            # Use Streamlit's image display for reliable rendering
            st.image(profile_image, width=120, use_container_width=False)
            profile_html = ""  # Let Streamlit handle the image
        except Exception as e:
            profile_html = f'<div class="initial">{initial}</div>'
    else:
        # Show initial if no image
        profile_html = f'<div class="initial">{initial}</div>'
    
    # Render Business Card - Use Streamlit image for reliable display
    st.markdown(f"""
    <div class="business-card">
        <div class="card-container">
            <div class="card-left">
                <div class="profile-pic-container">
                    {profile_html}
                </div>
                <p class="card-name">{name}</p>
                <p class="card-title">{role} • {company}</p>
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
                <button class="edit-profile-btn" onclick="document.getElementById('edit-profile-section').scrollIntoView({{behavior: 'smooth', block: 'center'}})">✏️ Edit Profile</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show welcome message
    st.caption(f"👋 Welcome, {name}!")

def render_edit_profile(user_info):
    """Render the edit profile section with image upload"""
    st.markdown('<div id="edit-profile-section"></div>', unsafe_allow_html=True)
    
    with st.expander("✏️ Edit Profile Information", expanded=st.session_state.get('show_edit_profile', False)):
        st.markdown("### Update Your Business Card Information")
        st.caption("📝 Update your profile details below")
        
        with st.form("edit_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("👤 Full Name", value=user_info.get('name', ''))
                new_email = st.text_input("✉️ Email", value=user_info.get('email', ''))
                new_phone = st.text_input("📞 Phone Number", value=user_info.get('phone', ''))
            
            with col2:
                new_company = st.text_input("🏢 Company Name", value=user_info.get('company_name', ''))
                new_address = st.text_input("📍 Address", value=user_info.get('address', ''))
                regions = ["Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNP", "Sidama", 
                          "Afar", "Benishangul-Gumuz", "Gambella", "Harari", "Dire Dawa", "Somali"]
                current_region = user_info.get('region', 'Addis Ababa')
                region_idx = regions.index(current_region) if current_region in regions else 0
                new_region = st.selectbox("🌍 Region", regions, index=region_idx)
            
            st.markdown("---")
            st.markdown("### 📷 Profile Picture")
            
            # Show current profile image using Streamlit
            current_image = user_info.get('profile_image', None)
            if current_image and os.path.exists(current_image):
                st.markdown("#### Current Profile Picture:")
                try:
                    st.image(current_image, width=150)
                except Exception as e:
                    st.warning("Could not load current image")
            
            # Image upload
            uploaded_file = st.file_uploader(
                "Upload New Profile Picture",
                type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff'],
                help="Supported formats: JPG, JPEG, PNG, GIF, WEBP, BMP, TIFF"
            )
            
            if uploaded_file is not None:
                st.markdown("#### Preview:")
                try:
                    st.image(uploaded_file, caption=f"📷 {uploaded_file.name}", width=200)
                    st.caption(f"Size: {uploaded_file.size / 1024:.1f} KB")
                except Exception as e:
                    st.error(f"Error displaying image: {e}")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
            with col2:
                cancel_btn = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if save_btn:
                if new_name and new_email:
                    try:
                        # Handle image upload
                        image_path = current_image
                        if uploaded_file is not None:
                            try:
                                # Create uploads directory
                                os.makedirs("uploads/profiles", exist_ok=True)
                                
                                # Generate unique filename
                                file_extension = uploaded_file.name.split('.')[-1].lower()
                                unique_filename = f"profile_{user_info['id']}_{uuid.uuid4().hex[:8]}.{file_extension}"
                                image_path = os.path.join("uploads/profiles", unique_filename)
                                
                                # Save the file
                                with open(image_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                
                                # Update profile image in database
                                success, msg = update_user_profile_image(user_info['id'], image_path)
                                if success:
                                    st.session_state.user_info['profile_image'] = image_path
                                    st.success("✅ Profile image updated!")
                                else:
                                    st.error(f"❌ {msg}")
                                    
                            except Exception as e:
                                st.error(f"Error saving image: {e}")
                                image_path = current_image
                        
                        # Update user information
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
                        st.error(f"❌ Error updating profile: {e}")
                else:
                    st.error("❌ Name and Email are required!")
            
            if cancel_btn:
                st.session_state.show_edit_profile = False
                st.rerun()
