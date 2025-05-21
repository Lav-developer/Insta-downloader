import streamlit as st
import instaloader
import os
from pathlib import Path
import time

# Set page configuration for better appearance
st.set_page_config(page_title="Instagram Downloader", page_icon="📸", layout="wide")

# Initialize Instaloader with video download enabled
L = instaloader.Instaloader(download_videos=True, save_metadata=False)

# Sidebar for navigation
st.sidebar.header("Navigation")
download_type = st.sidebar.radio("Download Type", ("Stories", "Reels"), help="Select whether to download stories or reels.")
login_required = st.sidebar.checkbox("Login to Instagram", help="Required for private accounts.")

# Login section in sidebar
if login_required:
    with st.sidebar.expander("Login Credentials"):
        ig_username = st.text_input("Instagram Username", placeholder="Enter your username")
        ig_password = st.text_input("Instagram Password", type="password", placeholder="Enter your password")
        if st.button("Login", key="login_button"):
            try:
                L.login(ig_username, ig_password)
                st.success("Logged in successfully!")
            except Exception as e:
                st.error(f"Login failed: {str(e)}")

# Main content
st.title("📸 Instagram Story and Reels Downloader")
st.markdown("Download Instagram stories or reels with ease. Enter the required details below and click **Download**.")

# Input form
with st.container():
    st.subheader("Download Details")
    col1, col2 = st.columns([3, 1])
    with col1:
        if download_type == "Stories":
            username = st.text_input("Instagram Username", placeholder="e.g., natgeo", help="Enter the username of the account whose stories you want to download.")
            post_url = ""
        else:
            post_url = st.text_input("Reel URL", placeholder="e.g., https://www.instagram.com/reel/C1234567890/", help="Enter the full URL of the reel.")
            username = ""
    with col2:
        st.write("")  # Spacer
        if st.button("Clear Inputs", key="clear_button"):
            username = ""
            post_url = ""
            st.rerun()

# Download functions
def download_stories(username):
    try:
        with st.spinner("Downloading stories..."):
            profile = instaloader.Profile.from_username(L.context, username)
            for story in L.get_stories(userids=[profile.userid]):
                for item in story.get_items():
                    L.download_storyitem(item, target=f"{download_dir}/{username}_stories")
            st.success(f"Stories downloaded to {download_dir}/{username}_stories")
            st.balloons()
    except Exception as e:
        st.error(f"Error downloading stories: {str(e)}")

def download_reels(post_url):
    try:
        with st.spinner("Downloading reel..."):
            post = instaloader.Post.from_shortcode(L.context, post_url.split("/")[-2])
            L.download_post(post, target=f"{download_dir}/reels")
            st.success(f"Reel downloaded to {download_dir}/reels")
            st.balloons()
    except Exception as e:
        st.error(f"Error downloading reel: {str(e)}")

# Download directory
download_dir = "downloads"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Download button
if st.button("Download", key="download_button", type="primary"):
    if download_type == "Stories" and username:
        download_stories(username)
    elif download_type == "Reels" and post_url:
        download_reels(post_url)
    else:
        st.warning("Please provide a valid username for stories or a post URL for reels.")

# Display downloaded files
with st.expander("📁 Downloaded Files", expanded=False):
    st.subheader("Available Downloads")
    if os.path.exists(download_dir):
        files = []
        for root, _, filenames in os.walk(download_dir):
            for file in filenames:
                if file.endswith((".mp4", ".jpg", ".jpeg")):
                    files.append(os.path.join(root, file))
        if files:
            for file_path in files:
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"Download {os.path.basename(file_path)}",
                        data=f,
                        file_name=os.path.basename(file_path),
                        mime="video/mp4" if file_path.endswith(".mp4") else "image/jpeg",
                        key=file_path
                    )
        else:
            st.write("No files downloaded yet.")
    else:
        st.write("No files downloaded yet.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center;">
        Developed by Lav Kush | 
        <a href="https://lav-developer.netlify.app" target="_blank">
            <button style="background-color: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer;">
                Portfolio
            </button>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)