import os
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips


def detect_scenes(video_path):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=30.0))
    base_timecode = video_manager.get_base_timecode()
    video_manager.set_downscale_factor()
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list(base_timecode)
    return [(scene[0].get_seconds(), scene[1].get_seconds()) for scene in scene_list]

def create_gifs(video_path, scenes, resolution, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    gif_paths = []
    for i, (start, end) in enumerate(scenes):
        clip = VideoFileClip(video_path).subclip(start, end).resize(newsize=resolution)
        gif_path = os.path.join(output_folder, f"scene_{i+1}.gif")
        clip.write_gif(gif_path, fps=10)
        gif_paths.append(gif_path)
    return gif_paths

def combine_selected_gifs(gif_paths):
    clips = [VideoFileClip(gif) for gif in gif_paths]
    final_clip = concatenate_videoclips(clips, method="compose")
    os.makedirs("combined_output", exist_ok=True)
    output_path = os.path.join("combined_output", "combined.gif")
    final_clip.write_gif(output_path, fps=10)
    return output_path

import yt_dlp
import os
import uuid

def download_tiktok_video(url):
    output_dir = "tiktok_downloads"
    os.makedirs(output_dir, exist_ok=True)
    unique_filename = str(uuid.uuid4()) + ".mp4"
    output_path = os.path.join(output_dir, unique_filename)

    ydl_opts = {
        'outtmpl': output_path,
        'quiet': True,
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'format': 'bestvideo+bestaudio/best'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return output_path
