import whisper


# Just do a for a loop,

# import whisper
# import os
#
# Получить список всех аудиофайлов в папке "data"
# audio_files = [f for f in os.listdir("data") if f.endswith('.wav')]
#
# Инициализировать пустой список для хранения транскрипций
# transcriptions = []
#
# Перебрать все аудиофайлы в папке "data"
# for audio_file in audio_files:
# audio_file_path = os.path.join("data", audio_file)
# result = model.transcribe(audio_file_path)
# transcription = str(result)
# transcriptions.append(transcription)


def speech_recognition(model='base'):
    speech_model = whisper.load_model(model)
    result = speech_model.transcribe('2022-01-10.mp3')
    # for f in *.wav ; do whisper $f --model medium ; done

    with open(f'{model}_transcribe.txt', 'w+') as file:
        file.write(result['text'])


def main():
    models = {1: 'tiny', 2: 'base', 3: 'small', 4: 'medium', 5: 'large'}

    for k, v in models.items():
        print(f'{k}:{v}')

    model = int(input('viberi model: '))

    if model not in models.keys():
        raise KeyError(f'Modeli {model} net v spiske')

    print('Idiyot transkribaciya...')
    speech_recognition(model=models[model])


if __name__ == '__main__':
    main()

# import whisper
# model = whisper.load_model("base")

# result = model.transcribe("/content/harvard.wav", verbose = True)
# print(result["text"])
