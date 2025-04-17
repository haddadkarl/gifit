import streamlit as st
import os
from moviepy.editor import VideoFileClip
from utils import detect_scenes, create_gifs, combine_selected_gifs, download_tiktok_video

st.set_page_config(page_title="Scene2GIF V2.5", layout="wide")

# Initialize session state
if "video_path" not in st.session_state:
    st.session_state.video_path = None
if "scene_list" not in st.session_state:
    st.session_state.scene_list = []
if "gif_paths" not in st.session_state:
    st.session_state.gif_paths = []
if "selected_gifs" not in st.session_state:
    st.session_state.selected_gifs = []

# Title
st.title("🎬 Gifit")

# TikTok video input (V2.5 feature)
st.markdown("#### Or paste a TikTok link")
tiktok_url = st.text_input("TikTok URL", placeholder="https://www.tiktok.com/...", label_visibility="collapsed")
if tiktok_url and st.button("Download from TikTok"):
    with st.spinner("Downloading TikTok video..."):
        try:
            downloaded_video_path = download_tiktok_video(tiktok_url)
            st.session_state["video_path"] = downloaded_video_path
            st.success("✅ TikTok video downloaded successfully!")
        except Exception as e:
            st.error(f"Download failed: {e}")

# Local upload option
uploaded_video = st.file_uploader("Upload a video", type=["mp4", "mov", "avi", "mkv"])
if uploaded_video:
    video_path = os.path.join("uploads", uploaded_video.name)
    os.makedirs("uploads", exist_ok=True)
    with open(video_path, "wb") as f:
        f.write(uploaded_video.read())
    st.session_state.video_path = video_path
    st.success("✅ Video uploaded successfully!")

# Show resolution and allow user to choose export size
if st.session_state.video_path:
    clip = VideoFileClip(st.session_state.video_path)
    width, height = clip.size
    st.markdown(f"**Original video resolution:** {width}x{height}")
    resolution = st.selectbox("Choose export resolution", options=["Original", "720p", "460p"])
    if resolution == "720p":
        target_resolution = (int(720 * width / height), 720)
    elif resolution == "460p":
        target_resolution = (int(460 * width / height), 460)
    else:
        target_resolution = clip.size

    # Detect Scenes
    if st.button("🎬 Detect Scenes"):
        st.info("🔍 Detecting scenes...")
        scene_list = detect_scenes(st.session_state.video_path)
        st.session_state.scene_list = scene_list
        st.success(f"✅ Detected {len(scene_list)} scenes.")

    # Generate GIFs
    if st.session_state.scene_list and st.button("🎞️ Generate GIFs from detected scenes"):
        st.info("🛠️ Creating GIFs...")
        gif_paths = create_gifs(
            st.session_state.video_path,
            st.session_state.scene_list,
            target_resolution,
            output_folder="gifs_output"
        )
        st.session_state.gif_paths = gif_paths
        st.success(f"✅ Generated {len(gif_paths)} GIFs.")

# Gallery & Download
if st.session_state.gif_paths:
    st.subheader("🖼️ Scene Gallery — Select GIFs to Combine")
    cols = st.columns(4)
    for i, gif_path in enumerate(st.session_state.gif_paths):
        with cols[i % 4]:
            st.image(gif_path, caption=os.path.basename(gif_path), use_container_width=True)
            if st.checkbox(f"Select {i+1}", key=f"gif_{i}"):
                if gif_path not in st.session_state.selected_gifs:
                    st.session_state.selected_gifs.append(gif_path)
            else:
                if gif_path in st.session_state.selected_gifs:
                    st.session_state.selected_gifs.remove(gif_path)

    # Download All
    os.makedirs("combined_output", exist_ok=True)
    with open("combined_output/all_gifs.zip", "wb") as f:
        import zipfile
        with zipfile.ZipFile(f, 'w') as zipf:
            for gif in st.session_state.gif_paths:
                zipf.write(gif, os.path.basename(gif))
    with open("combined_output/all_gifs.zip", "rb") as f:
        st.download_button("📦 Download All GIFs", f, file_name="all_gifs.zip")

    # Combine selected
    if st.session_state.selected_gifs:
        combined_path = combine_selected_gifs(st.session_state.selected_gifs)
        with open(combined_path, "rb") as f:
            st.download_button("✨ Download Combined GIF", f, file_name="combined.gif")
