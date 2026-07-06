"""Document upload and verification helpers."""
import base64
import streamlit as st
from utils.db_helpers import supabase, cached_get_profile


def check_verification_status(user_id):
    try:
        docs = supabase.table("verification_documents").select("*").eq("user_id", user_id).execute().data or []
        profile = cached_get_profile(user_id)
        is_verified = profile.get("is_verified", False) if profile else False
        return {
            "has_documents": len(docs) > 0,
            "is_verified": is_verified,
            "documents": docs,
            "can_transact": is_verified,
        }
    except Exception:
        return {"has_documents": False, "is_verified": False, "documents": [], "can_transact": False}


def upload_document(user_id, doc_type, file_bytes, file_name):
    try:
        doc_base64 = base64.b64encode(file_bytes).decode('utf-8')
        existing = supabase.table("verification_documents").select("*")\
            .eq("user_id", user_id).eq("document_type", doc_type).execute().data
        payload = {
            "user_id": user_id,
            "document_type": doc_type,
            "document_name": file_name,
            "document_url": f"uploaded_{file_name}",
            "document_base64": doc_base64,
            "file_size": len(file_bytes),
            "is_verified": False,
        }
        if existing:
            supabase.table("verification_documents").update(payload)\
                .eq("user_id", user_id).eq("document_type", doc_type).execute()
        else:
            supabase.table("verification_documents").insert(payload).execute()
        supabase.table("profiles").update({"documents_uploaded": True}).eq("id", user_id).execute()
        return True, "Document uploaded successfully!"
    except Exception as e:
        return False, f"Upload failed: {e}"


def render_document_upload(user_id, role):
    st.warning("⚠️ Verification Required — Upload documents to access full features.")
    st.info("Until verified, you can only browse products.")
    with st.container(border=True):
        st.subheader("📄 Upload Verification Documents")
        doc_type = st.selectbox(
            "Document Type",
            ["national_id", "business_license", "photo", "other"],
            format_func=lambda x: {
                "national_id": "🆔 National ID",
                "business_license": "📋 License",
                "photo": "📷 Photo",
                "other": "📄 Other",
            }.get(x, x),
            key=f"doc_type_{user_id}_{role}",
        )
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["jpg", "jpeg", "png", "pdf"],
            key=f"doc_upload_{user_id}_{role}",
        )
        if uploaded_file:
            st.info(f"Selected: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
            if st.button("📤 Upload Document", type="primary", use_container_width=True, key=f"upload_btn_{user_id}_{role}"):
                try:
                    file_bytes = uploaded_file.read()
                    success, msg = upload_document(user_id, doc_type, file_bytes, uploaded_file.name)
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
                except Exception as e:
                    st.error(f"Upload error: {e}")
        try:
            existing_docs = supabase.table("verification_documents").select("*").eq("user_id", user_id).execute().data or []
            if existing_docs:
                st.divider()
                st.markdown("**Your Uploaded Documents:**")
                for doc in existing_docs:
                    status_icon = "✅" if doc.get("is_verified") else "⏳"
                    st.caption(f"{status_icon} {doc.get('document_name')} ({doc.get('document_type')}) — {'Verified' if doc.get('is_verified') else 'Pending'}")
        except Exception as _doc_list_err:
            st.caption(f"Could not load document list: {_doc_list_err}")
