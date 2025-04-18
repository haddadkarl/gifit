import streamlit as st
import os
import shutil
from utils import detect_scenes, generate_gifs, combine_gifs, download_video_from_tiktok
import tempfile
import uuid

st.set_page_config(page_title="GifIt — Scene to GIF", layout="wide")
st.title("🎬 GifIt — Scene to GIF")

if 'gif_paths' not in st.session_state:
    st.session_state.gif_paths = []

if 'selected_gifs' not in st.session_state:
    st.session_state.selected_gifs = []

resolution = st.selectbox("Select GIF Resolution", ["original", "720p", "480p"], index=2)

upload_method = st.radio("Upload method", ("Upload file", "Paste TikTok link"), index=1)

video_file = None
temp_video_path = None

if upload_method == "Upload file":
    video_file = st.file_uploader("Upload a video file", type=["mp4", "mov"])
    if video_file:
        temp_dir = tempfile.mkdtemp()
        temp_video_path = os.path.join(temp_dir, f"{uuid.uuid4()}.mp4")
        with open(temp_video_path, "wb") as f:
            f.write(video_file.read())
else:
    link = st.text_input("Paste TikTok video link:")
    if link:
        temp_video_path = download_video_from_tiktok(link)
        if not temp_video_path:
            st.error("⚠️ Failed to fetch video. Please check the link.")

if temp_video_path and st.button("Detect Scenes"):
    scene_list = detect_scenes(temp_video_path)
    if not scene_list:
        st.error("No scenes detected.")
    else:
        st.session_state.gif_paths = generate_gifs(temp_video_path, scene_list, resolution=resolution)
        st.success(f"✅ Generated {len(st.session_state.gif_paths)} GIFs.")

if st.session_state.gif_paths:
    st.subheader("🖼️ Scene Gallery — Select GIFs to Combine")
    cols = st.columns(4)
    st.session_state.selected_gifs = []
    for i, gif_path in enumerate(st.session_state.gif_paths):
        with cols[i % 4]:
            st.image(gif_path, caption=os.path.basename(gif_path))
            if st.checkbox(f"Select {i+1}", key=f"gif_{i}"):
                st.session_state.selected_gifs.append(gif_path)

    if st.button("Download Combined Selected GIFs"):
        if not st.session_state.selected_gifs:
            st.warning("Please select at least one GIF.")
        else:
            combined_path = os.path.join(tempfile.gettempdir(), "combined.gif")
            combine_gifs(st.session_state.selected_gifs, combined_path)
            with open(combined_path, "rb") as f:
                st.download_button("⬇️ Download Combined GIF", f, file_name="combined.gif", mime="image/gif")

    if st.button("Download All GIFs as ZIP"):
        zip_path = os.path.join(tempfile.gettempdir(), "all_gifs.zip")
        shutil.make_archive(zip_path.replace('.zip', ''), 'zip', os.path.dirname(st.session_state.gif_paths[0]))
        with open(zip_path, "rb") as z:
            st.download_button("⬇️ Download All GIFs", z, file_name="all_gifs.zip", mime="application/zip")
