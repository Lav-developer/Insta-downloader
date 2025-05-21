import streamlit as st
import instaloader
import os
from pathlib import Path
import uuid
import shutil

# Set page configuration
st.set_page_config(page_title="Instagram Downloader", page_icon="📸", layout="centered")

# Initialize Instaloader
L = instaloader.Instaloader(
    download_videos=True,
    save_metadata=False,
    compress_json=False
)

# Main content
st.title("📸 Instagram Downloader")
st.markdown("Download Instagram stories or reels directly to your device.")

# Select download type
download_type = st.radio("What do you want to download?", ("Stories", "Reels"), horizontal=True)

# Login section
login_expander = st.expander("🔒 Login (for private accounts)")
with login_expander:
    ig_username = st.text_input("Instagram Username", placeholder="Enter your username")
    ig_password = st.text_input("Instagram Password", type="password", placeholder="Enter your password")
    if st.button("Login"):
        try:
            L.login(ig_username, ig_password)
            st.success("Logged in successfully!")
        except Exception as e:
            st.error(f"Login failed: {str(e)}")

# Input form
if download_type == "Stories":
    username = st.text_input("Account Username", placeholder="e.g., natgeo", help="Enter the username whose stories you want to download.")
    post_url = ""
else:
    post_url = st.text_input("Reel URL", placeholder="e.g., https://www.instagram.com/reel/C1234567890/", help="Enter the full URL of the reel.")
    username = ""

# Download functions with improved file handling
def download_stories(username):
    try:
        # Create a unique temp directory for this download
        temp_dir = f"temp_{username}_{uuid.uuid4().hex}"
        os.makedirs(temp_dir, exist_ok=True)
        
        with st.spinner("Fetching stories..."):
            profile = instaloader.Profile.from_username(L.context, username)
            downloaded_files = []
            
            for story in L.get_stories(userids=[profile.userid]):
                for item in story.get_items():
                    L.download_storyitem(item, target=temp_dir)
            
            # Collect downloaded files
            for file in Path(temp_dir).glob("*.*"):
                if file.suffix.lower() in [".mp4", ".jpg", ".jpeg", ".png"]:
                    downloaded_files.append(str(file))
            
            return downloaded_files, temp_dir
            
    except Exception as e:
        st.error(f"Error downloading stories: {str(e)}")
        return [], ""

def download_reels(post_url):
    try:
        # Create a unique temp directory for this download
        temp_dir = f"temp_reel_{uuid.uuid4().hex}"
        os.makedirs(temp_dir, exist_ok=True)
        
        with st.spinner("Fetching reel..."):
            shortcode = post_url.split("/")[-2]
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(post, target=temp_dir)
            
            # Collect downloaded files
            downloaded_files = []
            for file in Path(temp_dir).glob("*.*"):
                if file.suffix.lower() in [".mp4", ".jpg", ".jpeg", ".png"]:
                    downloaded_files.append(str(file))
            
            return downloaded_files, temp_dir
            
    except Exception as e:
        st.error(f"Error downloading reel: {str(e)}")
        return [], ""

# Initialize session state
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
if st.button("Download", type="primary"):
    st.session_state.downloaded_files = []
    
    if download_type == "Stories" and username:
        downloaded_files, temp_dir = download_stories(username)
        if downloaded_files:
            st.session_state.downloaded_files = downloaded_files
            st.session_state.temp_dirs.append(temp_dir)
            st.success(f"Found {len(downloaded_files)} story items!")
            st.balloons()
        else:
            st.warning("No stories found or could not download.")
            
    elif download_type == "Reels" and post_url:
        downloaded_files, temp_dir = download_reels(post_url)
        if downloaded_files:
            st.session_state.downloaded_files = downloaded_files
            st.session_state.temp_dirs.append(temp_dir)
            st.success("Reel downloaded successfully!")
            st.balloons()
        else:
            st.warning("No reel found or could not download.")
    else:
        st.warning("Please provide valid input.")

# Display downloaded files
if st.session_state.downloaded_files:
    st.subheader("Download Files")
    
    for file_path in st.session_state.downloaded_files:
        try:
            with open(file_path, "rb") as f:
                file_name = os.path.basename(file_path)
                file_ext = os.path.splitext(file_name)[1].lower()
                
                if file_ext == ".mp4":
                    mime_type = "video/mp4"
                    st.video(f.read())
                else:
                    mime_type = "image/jpeg"
                    st.image(f.read())
                
                f.seek(0)  # Reset file pointer
                st.download_button(
                    label=f"Download {file_name}",
                    data=f,
                    file_name=file_name,
                    mime=mime_type,
                    key=f"download_{uuid.uuid4().hex}"
                )
        except Exception as e:
            st.error(f"Error displaying file: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center;">
        Developed by Lav Kush | 
        <a href="https://lav-developer.netlify.app" target="_blank">Portfolio</a>
    </div>
    """,
    unsafe_allow_html=True
)