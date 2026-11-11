import os
import subprocess
import imageio_ffmpeg

def extract_audio(video_path, audio_path):
    if os.path.exists(audio_path):
        print(f"Аудиофайл {os.path.basename(audio_path)} уже существует и будет взят за основу")
    else:
        command = [
            imageio_ffmpeg.get_ffmpeg_exe(), "-y",
            "-loglevel", "quiet",  # Скрыть логи ffmpeg
            "-i", video_path,
            "-af", "afftdn",
            "-af", "loudnorm",
            "-vn",
            "-c:a", "libmp3lame",  # перевод в mp3
            "-b:a", "192k",
            audio_path
        ]
        print("Выделение аудио с помощью ffmpeg....")
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Аудио дорожка извлечена...")
    return audio_path