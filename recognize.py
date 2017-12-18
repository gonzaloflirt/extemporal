import ast, argparse, configparser, io, pickle
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from os import listdir, path

def transcribe(speechFile):
    print('transcribing ' + speechFile)

    client = speech.SpeechClient()

    with io.open(path.join(dataDir, speechFile + '.wav'), 'rb') as audioFile:
        content = audioFile.read()
    audio = types.RecognitionAudio(content = content)

    responses = {}
    for languageCode in languageCodes:

        config = types.RecognitionConfig(
            encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz = 16000,
            language_code = languageCode,
            enable_word_time_offsets = True,
            profanity_filter = False)

        responses[languageCode] = client.recognize(config, audio)

    responseFile = open(path.join(dataDir, speechFile + '.resp'), 'wb')
    pickle.dump(responses, responseFile)
    responseFile.close()

def filesToTranscribe():
    allFiles = [file for file in listdir(dataDir) if (path.isfile(path.join(dataDir, file)))]
    wavFiles = [path.splitext(file)[0] for file in allFiles if (file.endswith('.wav'))]
    responseFiles = [path.splitext(file)[0] for file in allFiles if (file.endswith('.resp'))]
    return [file for file in wavFiles if file not in responseFiles]

config = configparser.ConfigParser()
config.read('extemporal.config')
dataDir = config.get('folders', 'data')
languageCodes = ast.literal_eval(config.get('recognition', 'languages'))

[transcribe(speechFile) for speechFile in filesToTranscribe()]
