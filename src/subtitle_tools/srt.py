import os
from pathlib import Path
from .translate import translate


def srt_time(seconds):
    total_ms = round(seconds * 1000)
    hours, remaining_ms = divmod(total_ms, 3_600_000)
    minutes, remaining_ms = divmod(remaining_ms, 60_000)
    seconds, milliseconds = divmod(remaining_ms, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def build_srt(segments, subtitle_name):
    print(f"Сборка субтитров из транскрибации - {subtitle_name}")
    nonempty_segments = [segment for segment in segments if segment['text'].strip()]
    os.makedirs('tests/subtitles', exist_ok=True)
    with open(rf'tests/subtitles/{subtitle_name}.srt', 'w', encoding='UTF-8') as file:
        for number, segment in enumerate(nonempty_segments, start=1):
            subtitle_text = segment['text']
            start = srt_time(segment['start'])
            end = srt_time(segment['end'])
            file.write(f'{number}\n{start} --> {end}\n{subtitle_text}\n\n')
    return rf'tests/subtitles/{subtitle_name}.srt'

def build_translation(subtitle_path, target_language):
    print(f"Перевод {subtitle_path} на {target_language} язык")
    source_path = Path(subtitle_path)
    translated_subtitle_path = source_path.with_name(f"{source_path.stem}_{target_language}{source_path.suffix}")

    with open(source_path, "r", encoding="utf-8") as source:
        translation_result = translate(subtitle_path, target_language)
        with open(translated_subtitle_path, "w", encoding="utf-8") as output:
            for subtitle_index, block in enumerate(source.read().strip().split('\n\n')):
                block = block.splitlines()
                text = translation_result["subtitles"][subtitle_index]["text"]
                subtitle_block = f"{block[0]}\n{block[1]}\n{text}\n\n"
                output.write(subtitle_block)

    return translated_subtitle_path



