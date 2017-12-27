import ast, argparse, configparser, io, json, pickle
from watson_developer_cloud import SpeechToTextV1
from os import listdir, path

def transcribe(speechFile):
    print('transcribing ' + speechFile)

    client = SpeechToTextV1(
        username = config.get('recognition', 'username'),
        password = config.get('recognition', 'password'),
    )

    audio =  open(path.join(dataDir, speechFile + '.flac'), 'rb')

    responses = {}
    for languageCode in languageCodes:

        responses[languageCode] = client.recognize(audio, content_type = 'audio/flac',
            timestamps = True ,continuous  =True, max_alternatives = 1, model = languageCode)

    responseFile = open(path.join(dataDir, speechFile + '.resp'), 'wb')
    pickle.dump(responses, responseFile)
    responseFile.close()

def filesToTranscribe():
    allFiles = [file for file in listdir(dataDir) if (path.isfile(path.join(dataDir, file)))]
    flacFiles = [path.splitext(file)[0] for file in allFiles if (file.endswith('.flac'))]
    responseFiles = [path.splitext(file)[0] for file in allFiles if (file.endswith('.resp'))]
    return [file for file in flacFiles if file not in responseFiles]

config = configparser.ConfigParser()
config.read('extemporal.config')
dataDir = config.get('folders', 'data')
languageCodes = ast.literal_eval(config.get('recognition', 'languages'))

[transcribe(speechFile) for speechFile in filesToTranscribe()]
