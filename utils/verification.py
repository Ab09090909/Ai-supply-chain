"""Document upload and verification helpers."""
import base64
import logging
from typing import Dict, Any, List, Optional, Tuple
import streamlit as st
from utils.db_helpers import supabase, cached_get_profile, clear_data_cache

# Configure logging
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────
MAX_FILE_SIZE_MB = 10  # Maximum file size in MB
ALLOWED_FILE_TYPES = ["jpg", "jpeg", "png", "pdf", "gif", "webp"]
ALLOWED_MIME_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "pdf": "application/pdf",
    "gif": "image/gif",
    "webp": "image/webp"
}

DOCUMENT_TYPE_LABELS = {
    "national_id": "🆔 National ID",
    "business_license": "📋 Business License",
    "photo": "📷 Profile Photo",
    "passport": "🛂 Passport",
    "tax_id": "🧾 Tax ID",
    "other": "📄 Other"
}

DOCUMENT_TYPE_DESCRIPTIONS = {
    "national_id": "Upload a clear photo of your national ID card (front and back if needed)",
    "business_license": "Upload your business license or trade registration certificate",
    "photo": "Upload a recent passport-sized photo of yourself",
    "passport": "Upload a copy of your passport (photo page)",
    "tax_id": "Upload your tax identification certificate",
    "other": "Upload any other supporting documents"
}

# ─────────────────────────────────────────────────────────────
# VERIFICATION STATUS FUNCTIONS
# ─────────────────────────────────────────────────────────────

def check_verification_status(user_id: str) -> Dict[str, Any]:
    """
    Check the verification status of a user.
    
    Args:
        user_id: User ID to check
    
    Returns:
        Dict with verification status information
    """
    if not user_id:
        logger.warning("check_verification_status called with empty user_id")
        return {
            "has_documents": False,
            "is_verified": False,
            "documents": [],
            "can_transact": False,
            "has_pending": False
        }
    
    try:
        # Get documents
        response = supabase.table("verification_documents").select("*").eq("user_id", user_id).execute()
        docs = response.data if response else []
        
        # Get profile
        profile = cached_get_profile(user_id)
        is_verified = profile.get("is_verified", False) if profile else False
        
        # Check if any documents are pending verification
        has_pending = any(not doc.get("is_verified", False) for doc in docs)
        
        return {
            "has_documents": len(docs) > 0,
            "is_verified": is_verified,
            "documents": docs,
            "can_transact": is_verified,
            "has_pending": has_pending
        }
    except Exception as e:
        logger.error(f"Verification status check error for {user_id}: {e}")
        return {
            "has_documents": False,
            "is_verified": False,
            "documents": [],
            "can_transact": False,
            "has_pending": False
        }

def get_verified_documents(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all verified documents for a user.
    
    Args:
        user_id: User ID
    
    Returns:
        List of verified documents
    """
    try:
        response = supabase.table("verification_documents").select("*").eq("user_id", user_id).eq("is_verified", True).execute()
        return response.data if response else []
    except Exception as e:
        logger.error(f"Get verified documents error for {user_id}: {e}")
        return []

def get_pending_documents(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all pending documents for a user.
    
    Args:
        user_id: User ID
    
    Returns:
        List of pending documents
    """
    try:
        response = supabase.table("verification_documents").select("*").eq("user_id", user_id).eq("is_verified", False).execute()
        return response.data if response else []
    except Exception as e:
        logger.error(f"Get pending documents error for {user_id}: {e}")
        return []

# ─────────────────────────────────────────────────────────────
# DOCUMENT UPLOAD FUNCTIONS
# ─────────────────────────────────────────────────────────────

def upload_document(
    user_id: str,
    doc_type: str,
    file_bytes: bytes,
    file_name: str,
    mime_type: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Upload a verification document for a user.
    
    Args:
        user_id: User ID
        doc_type: Type of document (national_id, business_license, etc.)
        file_bytes: File content as bytes
        file_name: Original file name
        mime_type: MIME type of the file
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    if not user_id:
        return False, "User ID is required"
    
    if not file_bytes:
        return False, "File content is empty"
    
    # Validate file size
    file_size_mb = len(file_bytes) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size ({file_size_mb:.1f} MB) exceeds the {MAX_FILE_SIZE_MB} MB limit"
    
    try:
        # Encode file to base64
        doc_base64 = base64.b64encode(file_bytes).decode('utf-8')
        
        # Check for existing document
        existing_response = supabase.table("verification_documents").select("*").eq("user_id", user_id).eq("document_type", doc_type).execute()
        existing = existing_response.data if existing_response else []
        
        # Prepare payload
        payload = {
            "user_id": user_id,
            "document_type": doc_type,
            "document_name": file_name,
            "document_url": f"uploaded_{file_name}",
            "document_base64": doc_base64,
            "file_size": len(file_bytes),
            "mime_type": mime_type or "application/octet-stream",
            "is_verified": False,
            "uploaded_at": "now()"
        }
        
        # Insert or update
        if existing:
            response = supabase.table("verification_documents").update(payload).eq("user_id", user_id).eq("document_type", doc_type).execute()
            message = "Document updated successfully! It will be reviewed by an admin."
        else:
            response = supabase.table("verification_documents").insert(payload).execute()
            message = "Document uploaded successfully! It will be reviewed by an admin."
        
        # Update profile
        supabase.table("profiles").update({"documents_uploaded": True}).eq("id", user_id).execute()
        
        # Clear caches
        clear_data_cache()
        
        logger.info(f"Document uploaded for user {user_id}: {file_name} ({doc_type})")
        return True, message
        
    except Exception as e:
        logger.error(f"Document upload error for {user_id}: {e}")
        return False, f"Upload failed: {str(e)}"

def delete_document(document_id: str, user_id: str) -> Tuple[bool, str]:
    """
    Delete a verification document.
    
    Args:
        document_id: Document ID to delete
        user_id: User ID (for authorization)
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    if not document_id or not user_id:
        return False, "Missing required parameters"
    
    try:
        # Verify document belongs to user
        response = supabase.table("verification_documents").select("id").eq("id", document_id).eq("user_id", user_id).execute()
        if not response or not response.data:
            return False, "Document not found or you don't have permission to delete it"
        
        # Delete document
        supabase.table("verification_documents").delete().eq("id", document_id).execute()
        
        # Check if user still has any documents
        remaining = supabase.table("verification_documents").select("id").eq("user_id", user_id).execute()
        if not remaining or not remaining.data:
            supabase.table("profiles").update({"documents_uploaded": False}).eq("id", user_id).execute()
        
        # Clear caches
        clear_data_cache()
        
        logger.info(f"Document {document_id} deleted for user {user_id}")
        return True, "Document deleted successfully"
        
    except Exception as e:
        logger.error(f"Document delete error: {e}")
        return False, f"Delete failed: {str(e)}"

def verify_document(document_id: str, admin_user_id: str, is_verified: bool = True) -> Tuple[bool, str]:
    """
    Verify or reject a document (admin function).
    
    Args:
        document_id: Document ID to verify
        admin_user_id: Admin user ID (for auditing)
        is_verified: True to verify, False to reject
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    if not document_id:
        return False, "Document ID is required"
    
    try:
        # Update document verification status
        response = supabase.table("verification_documents").update({
            "is_verified": is_verified,
            "verified_by": admin_user_id,
            "verified_at": "now()"
        }).eq("id", document_id).execute()
        
        if is_verified:
            message = "Document verified successfully"
        else:
            message = "Document rejected"
        
        # Check if all documents are verified
        doc_response = supabase.table("verification_documents").select("id, is_verified").eq("id", document_id).execute()
        if doc_response and doc_response.data:
            user_id = doc_response.data[0].get("user_id")
            if user_id and is_verified:
                # Check if all documents for this user are verified
                all_docs = supabase.table("verification_documents").select("is_verified").eq("user_id", user_id).execute()
                if all_docs and all_docs.data:
                    all_verified = all(doc.get("is_verified", False) for doc in all_docs.data)
                    if all_verified:
                        supabase.table("profiles").update({"is_verified": True}).eq("id", user_id).execute()
                        logger.info(f"User {user_id} fully verified")
        
        # Clear caches
        clear_data_cache()
        
        logger.info(f"Document {document_id} {message} by admin {admin_user_id}")
        return True, message
        
    except Exception as e:
        logger.error(f"Document verification error: {e}")
        return False, f"Verification failed: {str(e)}"

# ─────────────────────────────────────────────────────────────
# UI RENDER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def render_document_upload(user_id: str, role: str) -> None:
    """
    Render document upload UI for verification.
    
    Args:
        user_id: User ID
        role: User role
    """
    # Check current status
    status = check_verification_status(user_id)
    
    if status["is_verified"]:
        st.success("✅ Your account is verified! You have full access to all features.")
        return
    
    st.warning("⚠️ Verification Required — Upload documents to access full features.")
    st.info("Until verified, you can only browse products. Upload the required documents below.")
    
    with st.container(border=True):
        st.subheader("📄 Upload Verification Documents")
        
        # Document type selection
        doc_type = st.selectbox(
            "Document Type",
            list(DOCUMENT_TYPE_LABELS.keys()),
            format_func=lambda x: DOCUMENT_TYPE_LABELS.get(x, x),
            key=f"doc_type_{user_id}"
        )
        
        # Show description
        st.caption(DOCUMENT_TYPE_DESCRIPTIONS.get(doc_type, ""))
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a file to upload",
            type=ALLOWED_FILE_TYPES,
            key=f"doc_upload_{user_id}",
            help=f"Maximum file size: {MAX_FILE_SIZE_MB}MB. Allowed formats: {', '.join(ALLOWED_FILE_TYPES)}"
        )
        
        if uploaded_file:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.info(f"Selected: {uploaded_file.name} ({file_size_mb:.1f} MB)")
            
            # Show preview for images
            if uploaded_file.type.startswith('image/'):
                st.image(uploaded_file, caption="Preview", width=200)
            
            if st.button("📤 Upload Document", type="primary", use_container_width=True, key=f"upload_btn_{user_id}"):
                if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                    st.error(f"File size exceeds {MAX_FILE_SIZE_MB}MB limit")
                else:
                    try:
                        file_bytes = uploaded_file.read()
                        success, msg = upload_document(
                            user_id,
                            doc_type,
                            file_bytes,
                            uploaded_file.name,
                            uploaded_file.type
                        )
                        if success:
                            st.success(msg)
                            st.balloons()
                            clear_data_cache()
                            st.rerun()
                        else:
                            st.error(msg)
                    except Exception as e:
                        logger.error(f"Upload error: {e}")
                        st.error(f"Upload error: {str(e)}")
        
        st.divider()
        
        # Show uploaded documents
        render_document_list(user_id)

def render_document_list(user_id: str) -> None:
    """
    Render list of uploaded documents.
    
    Args:
        user_id: User ID
    """
    try:
        response = supabase.table("verification_documents").select("*").eq("user_id", user_id).order("uploaded_at", desc=True).execute()
        docs = response.data if response else []
        
        if not docs:
            st.caption("No documents uploaded yet.")
            return
        
        st.markdown("**Your Uploaded Documents:**")
        for doc in docs:
            doc_type = doc.get("document_type", "unknown")
            label = DOCUMENT_TYPE_LABELS.get(doc_type, doc_type)
            doc_name = doc.get("document_name", "Untitled")
            is_verified = doc.get("is_verified", False)
            uploaded_at = doc.get("uploaded_at", "")
            
            # Status icon
            if is_verified:
                status_icon = "✅"
                status_text = "Verified"
                status_color = "green"
            else:
                status_icon = "⏳"
                status_text = "Pending Review"
                status_color = "orange"
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.caption(f"{status_icon} **{label}** — {doc_name}")
                if uploaded_at:
                    st.caption(f"📅 Uploaded: {uploaded_at[:16] if uploaded_at else 'N/A'}")
            with col2:
                if is_verified:
                    st.caption(f"🟢 {status_text}")
                else:
                    st.caption(f"🟡 {status_text}")
            with col3:
                # Delete button
                if st.button("🗑️", key=f"del_doc_{doc['id']}_{user_id}", help="Delete this document"):
                    success, msg = delete_document(doc["id"], user_id)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            
            # Show preview for images
            if doc.get("document_base64") and doc.get("mime_type", "").startswith("image/"):
                with st.expander("📷 Preview"):
                    st.image(f"data:{doc.get('mime_type', 'image/jpeg')};base64,{doc['document_base64']}", width=300)
            
            st.divider()
            
    except Exception as e:
        logger.error(f"Document list error: {e}")
        st.caption(f"Could not load document list: {str(e)}")

def render_verification_status(user_id: str, show_detailed: bool = True) -> None:
    """
    Render a simplified verification status badge.
    
    Args:
        user_id: User ID
        show_detailed: Whether to show detailed status
    """
    if not user_id:
        st.caption("⚠️ Not authenticated")
        return
    
    try:
        status = check_verification_status(user_id)
        
        if status.get("is_verified", False):
            st.success("✅ Verified Account")
            if show_detailed:
                st.caption("Your account is fully verified. You have access to all features.")
        elif status.get("has_documents", False):
            if status.get("has_pending", False):
                st.warning("⏳ Documents Pending Review")
                if show_detailed:
                    st.caption("Your documents are being reviewed by an admin. Please check back later.")
            else:
                st.info("📄 Documents Uploaded")
                if show_detailed:
                    st.caption("Your documents have been uploaded but verification is not yet complete.")
        else:
            st.info("📄 Verification Required")
            if show_detailed:
                st.caption("Upload the required documents to verify your account.")
    except Exception as e:
        logger.error(f"Verification status render error: {e}")
        st.caption("⚠️ Verification check unavailable")

def render_verification_badge(user_id: str) -> None:
    """
    Render a simple verification badge for display.
    
    Args:
        user_id: User ID
    """
    try:
        status = check_verification_status(user_id)
        if status.get("is_verified", False):
            st.markdown("🟢 Verified")
        elif status.get("has_documents", False):
            st.markdown("🟡 Pending")
        else:
            st.markdown("🔴 Unverified")
    except Exception:
        st.markdown("⚪ Unknown")

# ─────────────────────────────────────────────────────────────
# ADMIN FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_pending_verifications(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get all pending verification documents (admin function).
    
    Args:
        limit: Maximum number of documents to return
    
    Returns:
        List of pending documents with user info
    """
    try:
        response = supabase.table("verification_documents").select(
            "*, profiles(full_name, email, region, role)"
        ).eq("is_verified", False).order("uploaded_at", desc=True).limit(limit).execute()
        return response.data if response else []
    except Exception as e:
        logger.error(f"Get pending verifications error: {e}")
        return []

def render_admin_verification_panel() -> None:
    """
    Render admin verification panel for reviewing documents.
    """
    st.subheader("🛡️ Pending Verifications")
    
    pending = get_pending_verifications()
    
    if not pending:
        st.info("No pending verification documents.")
        return
    
    st.caption(f"Showing {len(pending)} pending document(s)")
    
    for doc in pending:
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                doc_type = doc.get("document_type", "unknown")
                label = DOCUMENT_TYPE_LABELS.get(doc_type, doc_type)
                st.markdown(f"**{label}**")
                
                # User info
                profile = doc.get("profiles", {})
                st.caption(f"👤 {profile.get('full_name', 'Unknown')}")
                st.caption(f"📧 {profile.get('email', 'No email')}")
                st.caption(f"📍 {profile.get('region', 'N/A')}")
                st.caption(f"📅 Uploaded: {doc.get('uploaded_at', '')[:16] if doc.get('uploaded_at') else 'N/A'}")
                
                # Document preview
                if doc.get("document_base64") and doc.get("mime_type", "").startswith("image/"):
                    with st.expander("📷 Preview Document"):
                        try:
                            st.image(f"data:{doc.get('mime_type', 'image/jpeg')};base64,{doc['document_base64']}", width=300)
                        except Exception as e:
                            st.error(f"Preview error: {e}")
            
            with col2:
                # Approve button
                if st.button("✅ Approve", key=f"verify_{doc['id']}", use_container_width=True):
                    admin_id = st.session_state.user.id
                    success, msg = verify_document(doc["id"], admin_id, True)
                    if success:
                        st.success(msg)
                        clear_data_cache()
                        st.rerun()
                    else:
                        st.error(msg)
            
            with col3:
                # Reject button
                if st.button("❌ Reject", key=f"reject_{doc['id']}", use_container_width=True):
                    admin_id = st.session_state.user.id
                    success, msg = verify_document(doc["id"], admin_id, False)
                    if success:
                        st.warning(msg)
                        clear_data_cache()
                        st.rerun()
                    else:
                        st.error(msg)
