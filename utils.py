import os
import cv2
import shutil
import tempfile
from moviepy.editor import VideoFileClip, concatenate_videoclips
from scenedetect import SceneManager, open_video, ContentDetector
from scenedetect.scene_manager import save_images
import yt_dlp


def download_tiktok_video(tiktok_url, download_dir):
    video_path = os.path.join(download_dir, "tiktok_video.mp4")
    ydl_opts = {
        'outtmpl': video_path,
        'format': 'best[ext=mp4]',
        'quiet': True,
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([tiktok_url])
    return video_path


def detect_scenes(video_path, output_dir):
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())
    scene_manager.detect_scenes(video)
    scene_list = scene_manager.get_scene_list()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    scene_paths = []
    for i, (start_time, end_time) in enumerate(scene_list):
        start_seconds = start_time.get_seconds()
        end_seconds = end_time.get_seconds()

        clip = VideoFileClip(video_path).subclip(start_seconds, end_seconds)
        scene_path = os.path.join(output_dir, f"scene_{i + 1}.gif")

        # Preserve aspect ratio
        width, height = clip.size
        clip.write_gif(scene_path, program='imageio', fps=10)
        scene_paths.append(scene_path)

    return scene_paths


def generate_gifs(video_path, output_dir, resolution='original'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    clip = VideoFileClip(video_path)
    width, height = clip.size

    if resolution == '720p':
        target_width = 720
    elif resolution == '480p':
        target_width = 480
    else:
        target_width = width  # Original

    scene_paths = detect_scenes(video_path, output_dir)
    resized_paths = []

    for path in scene_paths:
        gif_clip = VideoFileClip(path)
        if target_width != width:
            gif_clip = gif_clip.resize(width=target_width)
        output_path = path  # Overwrite same file
        gif_clip.write_gif(output_path, program='imageio', fps=10)
        resized_paths.append(output_path)

    return resized_paths


def combine_gifs(gif_paths, output_path="combined.gif"):
    clips = [VideoFileClip(path) for path in gif_paths]
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_gif(output_path, fps=10)
    return output_path
