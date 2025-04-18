
import streamlit as st
import os
import shutil
from utils import detect_scenes, generate_gifs, combine_gifs

st.set_page_config(page_title="GifIt — Scene to GIF", layout="wide")
st.title("🎬 GifIt — Scene to GIF")

# Initialize session state
if "video_path" not in st.session_state:
    st.session_state.video_path = None
if "scene_list" not in st.session_state:
    st.session_state.scene_list = []
if "gif_paths" not in st.session_state:
    st.session_state.gif_paths = []
if "selected_gifs" not in st.session_state:
    st.session_state.selected_gifs = []

# Upload video
uploaded_video = st.file_uploader("Upload a video", type=["mp4", "mov", "avi", "mkv"])
if uploaded_video is not None:
    video_path = os.path.join("uploads", uploaded_video.name)
    os.makedirs("uploads", exist_ok=True)
    with open(video_path, "wb") as f:
        f.write(uploaded_video.read())
    st.session_state.video_path = video_path
    st.success(f"Uploaded {uploaded_video.name}")

# Select resolution
resolution = st.selectbox("Select GIF resolution", ["Original", "720p", "480p"])

# Detect scenes
if st.session_state.video_path:
    if st.button("🎯 Detect Scenes"):
        st.session_state.scene_list = detect_scenes(st.session_state.video_path)
        st.success(f"Detected {len(st.session_state.scene_list)} scenes.")

    # Generate GIFs
    if st.session_state.scene_list:
        if st.button("📦 Generate GIFs from detected scenes"):
            shutil.rmtree("gifs_output", ignore_errors=True)
            os.makedirs("gifs_output", exist_ok=True)
            st.session_state.gif_paths = generate_gifs(
                st.session_state.video_path,
                st.session_state.scene_list,
                resolution,
                "gifs_output",
            )
            st.success(f"Generated {len(st.session_state.gif_paths)} GIFs.")

# Display the GIFs in gallery
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

# Combine selected GIFs
if st.session_state.selected_gifs:
    st.subheader("📎 Combine Selected GIFs")
    if st.button("🔗 Combine Selected"):
        combined_path = combine_gifs(st.session_state.selected_gifs, "gifs_output")
        st.success("Combined GIF created!")
        with open(combined_path, "rb") as f:
            st.download_button("Download Combined GIF", f, file_name="combined.gif")
