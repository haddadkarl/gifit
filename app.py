import streamlit as st
import os
import shutil
from utils import detect_scenes, generate_gifs, combine_gifs
from pytube import YouTube
import tempfile

st.set_page_config(page_title="GifIt — Scene to GIF", layout="wide")
st.title("🎬 GifIt — Scene to GIF")

# Session state setup
if "video_path" not in st.session_state:
    st.session_state.video_path = None
    st.session_state.scene_list = []
    st.session_state.gif_paths = []
    st.session_state.selected_gifs = []
    st.session_state.tiktok_link = ""
    st.session_state.resolution = None

# Resolution options
res_options = {"Original": None, "720p": (1280, 720), "480p": (854, 480), "360p": (640, 360)}
res_choice = st.selectbox("Select GIF Resolution", list(res_options.keys()))
st.session_state.resolution = res_options[res_choice]

# TikTok URL input or file upload
video_source = st.radio("Upload method", ["Upload file", "Paste TikTok link"])
if video_source == "Upload file":
    uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov"])
    if uploaded_file:
        tmp_dir = tempfile.mkdtemp()
        video_path = os.path.join(tmp_dir, uploaded_file.name)
        with open(video_path, "wb") as f:
            f.write(uploaded_file.read())
        st.session_state.video_path = video_path
elif video_source == "Paste TikTok link":
    link = st.text_input("Paste TikTok video link:")
    if link:
        try:
            yt = YouTube(link)
            stream = yt.streams.filter(file_extension='mp4', resolution="360p").first()
            tmp_dir = tempfile.mkdtemp()
            video_path = os.path.join(tmp_dir, "tiktok_video.mp4")
            stream.download(output_path=tmp_dir, filename="tiktok_video.mp4")
            st.session_state.video_path = video_path
            st.success("TikTok video downloaded!")
        except Exception as e:
            st.error(f"Failed to fetch video: {e}")

# Detect scenes
if st.session_state.video_path and st.button("🎞️ Detect Scenes"):
    st.session_state.scene_list = detect_scenes(st.session_state.video_path)
    st.success(f"Detected {len(st.session_state.scene_list)} scenes.")

# Generate GIFs
if st.session_state.scene_list and st.button("🎬 Generate GIFs"):
    st.session_state.gif_paths = generate_gifs(
        st.session_state.video_path,
        st.session_state.scene_list,
        output_dir="gifs_output",
        resolution=st.session_state.resolution,
    )
    st.success(f"Generated {len(st.session_state.gif_paths)} GIFs.")

# Display GIFs with selection checkboxes
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

# Combine and download buttons
if st.session_state.selected_gifs:
    if st.button("🧩 Combine Selected GIFs"):
        output_path = "gifs_output/combined.gif"
        combine_gifs(st.session_state.selected_gifs, output_path)
        with open(output_path, "rb") as f:
            st.download_button("⬇️ Download Combined GIF", f, file_name="combined.gif")

if st.session_state.gif_paths:
    if st.button("⬇️ Download All GIFs as ZIP"):
        import zipfile
        zip_path = "gifs_output/all_gifs.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for gif in st.session_state.gif_paths:
                zipf.write(gif, os.path.basename(gif))
        with open(zip_path, "rb") as f:
            st.download_button("⬇️ Download ZIP", f, file_name="all_gifs.zip")
