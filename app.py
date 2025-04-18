import streamlit as st
import os
import shutil
from utils import detect_scenes, generate_gifs, combine_gifs

st.set_page_config(page_title="GifIt — Scene to GIF", layout="wide")
st.title("🎬 GifIt — Scene to GIF")

# Initialize session state
if 'scene_list' not in st.session_state:
    st.session_state.scene_list = []
if 'gif_paths' not in st.session_state:
    st.session_state.gif_paths = []
if 'selected_gifs' not in st.session_state:
    st.session_state.selected_gifs = []

# Upload video
uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])
resolution = st.selectbox("Select resolution for GIFs", ["Original", "720", "460"])

if uploaded_file:
    # Clear previous session state
    st.session_state.scene_list = []
    st.session_state.gif_paths = []
    st.session_state.selected_gifs = []

    # Save uploaded video
    os.makedirs("uploads", exist_ok=True)
    video_path = os.path.join("uploads", uploaded_file.name)
    with open(video_path, "wb") as f:
        f.write(uploaded_file.read())
    st.video(video_path)

    # Detect scenes
    if st.button("Detect Scenes"):
        st.session_state.scene_list = detect_scenes(video_path)
        st.success(f"✅ Detected {len(st.session_state.scene_list)} scenes.")

    # Generate GIFs
    if st.session_state.scene_list:
        if st.button("Generate GIFs"):
            os.makedirs("gifs_output", exist_ok=True)
            st.session_state.gif_paths = generate_gifs(video_path, st.session_state.scene_list, resolution)
            st.success(f"✅ Generated {len(st.session_state.gif_paths)} GIFs.")

# Display GIFs and select for combination
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
if len(st.session_state.selected_gifs) > 1:
    if st.button("Generate Combined GIF"):
        combined_path = combine_gifs(st.session_state.selected_gifs)
        st.success("🎉 Combined GIF generated!")
        st.image(combined_path)
        with open(combined_path, "rb") as f:
            st.download_button("Download Combined GIF", f, file_name="combined.gif", mime="image/gif")