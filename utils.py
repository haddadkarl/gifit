import os
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from moviepy.editor import VideoFileClip
import imageio

def detect_scenes(video_path):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())
    video_manager.set_downscale_factor()
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list()
    return [(start.get_seconds(), end.get_seconds()) for start, end in scene_list]

def generate_gifs(video_path, scene_list, resolution):
    gif_paths = []
    video = VideoFileClip(video_path)
    for i, (start, end) in enumerate(scene_list):
        clip = video.subclip(start, end)
        if resolution == "720":
            clip = clip.resize(height=720)
        elif resolution == "460":
            clip = clip.resize(height=460)
        output_path = f"gifs_output/scene_{i+1}.gif"
        clip.write_gif(output_path)
        gif_paths.append(output_path)
    return gif_paths

def combine_gifs(gif_paths):
    images = []
    for gif in gif_paths:
        reader = imageio.get_reader(gif)
        images.extend([frame for frame in reader])
        reader.close()
    output_path = "gifs_output/combined.gif"
    imageio.mimsave(output_path, images, format='GIF', duration=0.2)
    return output_path