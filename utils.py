import os
import cv2
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from moviepy.editor import VideoFileClip, concatenate_videoclips
from PIL import Image


def detect_scenes(video_path):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=30.0))

    base_timecode = video_manager.get_base_timecode()
    video_manager.set_downscale_factor()
    video_manager.start()

    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list(base_timecode)

    return [(start.get_seconds(), end.get_seconds()) for start, end in scene_list]


def generate_gifs(video_path, scene_list, output_dir, resolution=None):
    os.makedirs(output_dir, exist_ok=True)
    gif_paths = []

    for i, (start_time, end_time) in enumerate(scene_list):
        clip = VideoFileClip(video_path).subclip(start_time, end_time)
        if resolution:
            clip = clip.resize(height=resolution[1])
        gif_path = os.path.join(output_dir, f"scene_{i+1}.gif")
        clip.write_gif(gif_path, fps=8)
        gif_paths.append(gif_path)

    return gif_paths


def combine_gifs(gif_paths, output_path):
    imgs = [Image.open(gif) for gif in gif_paths]
    durations = [img.info.get('duration', 100) for img in imgs]

    all_frames = []
    for img in imgs:
        img.seek(0)
        try:
            while True:
                all_frames.append(img.copy())
                img.seek(img.tell() + 1)
        except EOFError:
            pass

    all_frames[0].save(
        output_path,
        save_all=True,
        append_images=all_frames[1:],
        loop=0,
        duration=sum(durations) // len(durations),
        disposal=2,
    )
