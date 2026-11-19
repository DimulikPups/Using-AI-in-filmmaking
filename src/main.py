import shutil
import subprocess
import tempfile
from pathlib import Path

import gradio as gr
import requests

from ffmpeg_tools.ffmpeg import get_audio, insert_subtitles
from src.subtitle_tools.srt import build_srt, split_sentences
from src.subtitle_tools.translate import translate
from src.transcribe_tools.transcribe import transcribe


def process_video(input_video, translate_languages, background, font_size, progress=gr.Progress()):
    if not input_video:
        raise gr.Error('Для начала загрузите видео!')

    process_folder = Path(tempfile.mkdtemp(prefix='subs-'))
    source_path = process_folder / ('video' + Path(input_video).suffix.lower())

    shutil.copyfile(input_video, source_path)

    try:
        progress(0.1, desc='Извлечение аудио')

        audio_path = str(process_folder / 'audio.mp3')
        get_audio(str(source_path), audio_path)

        progress(0.25, desc='Распознавание речи')

        result = transcribe(audio_path)
        words = result.get('words') # Возвращает метки по каждому слову

        if not words:
            raise gr.Error('Routerai не вернул метки слов')

        sentences = split_sentences(words)
        if not sentences:
            raise gr.Error('В аудио не обнаружена речь')

        subtitle_path = Path(build_srt(sentences, 'generated_subs', process_folder))

        translated_files = []
        video_files = []

        for index, to_language in enumerate(translate_languages):
            progress(0.4 + 0.5 * index / len(translate_languages), desc=f'Переводится на {to_language}')

            translated_subs = translate(str(subtitle_path), to_language)['subtitles'] # Возвращает json в виде {"subtitles": []}

            translations = {item['id']: item['text'] for item in translated_subs} # Распаковка json в словарик с айди

            all_subs_cnt = set(range(1, len(sentences) + 1))

            # Проверка на совпадение количества переведённых строк и оригинальных строк
            if len(translated_subs) != len(all_subs_cnt) or set(translations) != all_subs_cnt:
                raise gr.Error(f'Нейросеть вернула неполный перевод: {to_language}. Попробуйте ещё раз.')

            translated_subs_path = process_folder / f'{to_language}.srt'

            blocks = []
            # Собираем блоки субтитров на основе исходных, заменяя текст оригинала на переводы из translations (id: text)
            for block in subtitle_path.read_text(encoding='utf-8').strip().split('\n\n'):
                lines = block.splitlines()
                blocks.append(f'{lines[0]}\n{lines[1]}\n{translations[int(lines[0])].strip()}\n\n')

            translated_subs_path.write_text(''.join(blocks), encoding='utf-8')
            translated_files.append(str(translated_subs_path))

            progress(0.4 + 0.5 * (index + 0.5) / len(translate_languages), desc=f'Создание видео: {to_language}')

            video_files.append(insert_subtitles(source_path, translated_subs_path, background, font_size))

        if not video_files:
            progress(0.75, desc='Добавление субтитров в видео')

            video_files.append(insert_subtitles(source_path, subtitle_path, background, font_size))

        progress(1, desc='Готово')

        return video_files[0]

    except gr.Error:
        raise gr.Error('Произошла непредвиденная ошибка!')


with gr.Blocks() as app:
    gr.Markdown('Загрузите видео, чтобы распознать речь, на её основе сгенерировать субтитры и, по желанию, перевести их!')
    with gr.Row():
        with gr.Column():
            video = gr.Video(label='Исходное видео', sources=['upload'])
            langs = gr.Dropdown(['английский', 'русский', 'испанский', 'немецкий', 'французский'], value=[], multiselect=True, label='Языки перевода',
                                info='Оставьте пустым, чтобы сохранить субтитры на языке оригинала.')
            subs_background = gr.Checkbox(value=True, label='Добавить чёрный фон для субтитров')
            font_size = gr.Slider(10, 40, value=16, step=1, label='Размер субтитров')
            submit = gr.Button('Создать субтитры', variant='primary')
        with gr.Column():
            output_video = gr.Video(label='Сгенерированное видео')
    submit.click(process_video, [video, langs, subs_background, font_size], output_video)
    app.launch(share=True)
