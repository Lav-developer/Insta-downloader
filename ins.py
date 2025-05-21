import streamlit as st
import instaloader
import os
from pathlib import Path
import uuid
import shutil

# Set page configuration
st.set_page_config(page_title="Instagram Reel Downloader", page_icon="📸", layout="centered")

# Initialize Instaloader
@st.cache_resource
def get_instaloader():
    return instaloader.Instaloader(
        download_videos=True,
        save_metadata=False,
        compress_json=False,
        request_timeout=60
    )

L = get_instaloader()

# Main content
st.title("📸 Instagram Reel Downloader")
st.markdown("Download Instagram reels directly from public links")

# Input form
post_url = st.text_input("Reel URL", 
                        placeholder="e.g., https://www.instagram.com/reel/C1234567890/", 
                        help="Enter the full URL of the reel")

def download_reel(post_url):
    try:
        # Create temp directory
        temp_dir = f"temp_reel_{uuid.uuid4().hex}"
        os.makedirs(temp_dir, exist_ok=True)
        
        with st.spinner("Downloading reel..."):
            # Extract shortcode from URL
            shortcode = post_url.split("/")[-2]
            
            # Get the post
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            # Download the reel
            L.download_post(post, target=temp_dir)
            
            # Find downloaded files
            downloaded_files = []
            for file in Path(temp_dir).glob("*.*"):
                if file.suffix.lower() in [".mp4", ".jpg", ".jpeg", ".png"]:
                    downloaded_files.append(str(file))
            
            return downloaded_files, temp_dir
            
    except Exception as e:
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise e

# Session state management
if "downloaded_files" not in st.session_state:
    st.session_state.downloaded_files = []
if "temp_dirs" not in st.session_state:
    st.session_state.temp_dirs = []

# Clean up previous temp directories
for temp_dir in st.session_state.temp_dirs:
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except:
        pass
st.session_state.temp_dirs = []

# Download button
if st.button("Download Reel", type="primary"):
    st.session_state.downloaded_files = []
    
    try:
        if post_url:
            downloaded_files, temp_dir = download_reel(post_url)
            if downloaded_files:
                st.session_state.downloaded_files = downloaded_files
                st.session_state.temp_dirs.append(temp_dir)
                st.success("✅ Reel downloaded successfully!")
                st.balloons()
            else:
                st.warning("Could not download the reel")
        else:
            st.warning("Please enter a valid reel URL")
            
    except Exception as e:
        st.error(f"Download failed: {str(e)}")

# Display downloaded media
if st.session_state.downloaded_files:
    st.subheader("Download Options")
    
    for file_path in st.session_state.downloaded_files:
        try:
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Only show preview for video files
            if file_ext == ".mp4":
                st.video(file_path)
            
            # Download button for all file types
            with open(file_path, "rb") as f:
                st.download_button(
                    label=f"Download {file_name}",
                    data=f,
                    file_name=file_name,
                    mime="video/mp4" if file_ext == ".mp4" else "image/jpeg",
                    key=f"dl_{uuid.uuid4().hex}"
                )
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center;">
    Developed by Lav Kush | 
    <a href="https://lav-developer.netlify.app" target="_blank">Portfolio</a>
</div>
""", unsafe_allow_html=True)