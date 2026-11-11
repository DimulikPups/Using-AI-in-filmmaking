from subtitle_tools.srt import *
from ffmpeg_tools.ffmpeg import *
from transcribe_tools.transcribe import transcribe

audio_path = extract_audio(r'tests/example_video/Саратовский государственный университет.mp4',
                           r'tests/extracted_audio/extracted_audio.mp3')

transcription_result = transcribe(audio_path)

subtitle_path = build_srt(transcription_result['segments'], os.path.splitext(os.path.basename(audio_path))[0])
print(f"Субтитры были успешно созданы:\t{subtitle_path}")
translated_subtitle_path = build_translation(subtitle_path, "английский")
print(f"Перевод создан: {translated_subtitle_path}")
