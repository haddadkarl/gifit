import streamlit as st
import os
import shutil
from utils import detect_scenes, generate_gifs, combine_gifs, download_tiktok_video
import tempfile
import uuid

st.set_page_config(page_title="Gifit", layout="wide")
st.title("🎬 Gifit")

# --- Session state initialization ---
if "video_path" not in st.session_state:
    st.session_state.video_path = None
if "gif_paths" not in st.session_state:
    st.session_state.gif_paths = []
if "selected_gifs" not in st.session_state:
    st.session_state.selected_gifs = []
if "video_uploaded" not in st.session_state:
    st.session_state.video_uploaded = False

# --- Video upload UI ---
st.markdown("### Select GIF Resolution")
resolution = st.selectbox("Select GIF Resolution", ["Original", "720p", "460p"], label_visibility="collapsed")

st.markdown("### Upload Method")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4"], label_visibility="collapsed")
with col2:
    tiktok_link = st.text_input("Paste a TikTok video link", placeholder="https://www.tiktok.com/...", label_visibility="collapsed")

# --- Handle video upload or TikTok link ---
if uploaded_file:
    temp_file_path = os.path.join("temp", f"{uuid.uuid4()}.mp4")
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.read())
    st.session_state.video_path = temp_file_path
    st.session_state.video_uploaded = True
    st.success("✅ Video file uploaded successfully.")

elif tiktok_link:
    try:
        with st.spinner("Downloading video from TikTok..."):
            clean_link = tiktok_link.split("?")[0]
            download_dir = tempfile.mkdtemp()
            st.session_state.video_path = download_tiktok_video(clean_link, download_dir)
            st.session_state.video_uploaded = True
            st.success("✅ TikTok video downloaded successfully.")
    except Exception as e:
        st.error(f"Failed to fetch video: {str(e)}")
        st.stop()

# --- Detect scenes ---
if st.session_state.video_uploaded and st.button("🎬 Detect Scenes"):
    st.session_state.gif_paths = detect_scenes(st.session_state.video_path, resolution.lower())
    st.session_state.selected_gifs = []
    st.success(f"✅ Generated {len(st.session_state.gif_paths)} GIFs.")

# --- Display the GIFs in gallery ---
if st.session_state.gif_paths:
    st.subheader("🖼️ Scene Gallery — Select GIFs to Combine")
    cols = st.columns(4)
    for i, gif_path in enumerate(st.session_state.gif_paths):
        with cols[i % 4]:
            st.image(gif_path, caption=os.path.basename(gif_path))
            if st.checkbox(f"Select {i+1}", key=f"gif_{i}"):
                if gif_path not in st.session_state.selected_gifs:
                    st.session_state.selected_gifs.append(gif_path)
            else:
                if gif_path in st.session_state.selected_gifs:
                    st.session_state.selected_gifs.remove(gif_path)

    # --- Download all GIFs ---
    if st.button("⬇️ Download All GIFs"):
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "all_gifs.zip")
            shutil.make_archive(zip_path.replace(".zip", ""), 'zip', root_dir=os.path.dirname(st.session_state.gif_paths[0]))
            with open(zip_path, "rb") as f:
                st.download_button("📦 Download All GIFs", f, file_name="all_gifs.zip", mime="application/zip")

    # --- Combine selected GIFs ---
    if st.session_state.selected_gifs:
        if st.button("📦 Combine Selected GIFs"):
            combined_path = combine_gifs(st.session_state.selected_gifs)
            if combined_path:
                with open(combined_path, "rb") as f:
                    st.download_button("⬇️ Download Combined GIF", f, file_name="combined.gif", mime="image/gif")
