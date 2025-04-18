import os
import yt_dlp
import tempfile
import cv2
import shutil
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from moviepy.editor import VideoFileClip
from PIL import Image

def download_video_from_tiktok(url):
    try:
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, '%(id)s.%(ext)s')
        ydl_opts = {
            'outtmpl': output_template,
            'format': 'mp4/best',
            'quiet': True,
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info_dict)
        return video_path
    except Exception as e:
        print(f"Error downloading TikTok video: {e}")
        return None

def detect_scenes(video_path):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())
    video_manager.set_downscale_factor()
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list()
    return scene_list

def generate_gifs(video_path, scene_list, resolution='480p'):
    temp_dir = tempfile.mkdtemp()
    output_paths = []
    clip = VideoFileClip(video_path)

    res_map = {
        '480p': (854, 480),
        '720p': (1280, 720),
        'original': None
    }

    for i, (start, end) in enumerate(scene_list):
        subclip = clip.subclip(start.get_seconds(), end.get_seconds())
        if resolution != 'original':
            subclip = subclip.resize(newsize=res_map[resolution])
        gif_path = os.path.join(temp_dir, f'scene_{i+1}.gif')
        subclip.write_gif(gif_path, program='imageio')
        output_paths.append(gif_path)

    return output_paths

def combine_gifs(gif_paths, output_path='combined.gif'):
    images = [Image.open(g) for g in gif_paths]
    images[0].save(output_path, save_all=True, append_images=images[1:], loop=0, duration=500)
    return output_path
