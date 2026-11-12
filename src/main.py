from subtitle_tools.srt import *
from ffmpeg_tools.ffmpeg import *
from transcribe_tools.transcribe import transcribe

video_path = r'tests/example_video/Саратовский государственный университет.mp4'
audio_path = extract_audio(video_path,
                           r'tests/extracted_audio/extracted_audio.mp3')

transcription_result = transcribe(audio_path)
words = transcription_result['words']
if not words:
    raise ValueError("Слова не были найдены в разметке от Whisper")

processed_segments = split_words(words)
subtitle_path = build_srt(processed_segments, os.path.splitext(os.path.basename(audio_path))[0])
print(f"Субтитры были успешно созданы:\t{subtitle_path}")
translated_subtitle_path = build_translation(subtitle_path, "английский")
print(f"Перевод создан: {translated_subtitle_path}")

video_with_subtitles = insert_subtitles(video_path, translated_subtitle_path, black_background=True)
print(f"Видео с субтитрами создано: {video_with_subtitles}")
