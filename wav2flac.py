import configparser
from os import listdir, path
from pydub import AudioSegment

def convert(file):
    data = AudioSegment.from_wav(path.join(dataDir, file) + '.wav')
    data.set_frame_rate(16000).export(path.join(dataDir, file) + '.flac', format = 'flac')

def filesToConvert():
    allFiles = [file for file in listdir(dataDir) if (path.isfile(path.join(dataDir, file)))]
    wavFiles = [path.splitext(file)[0] for file in allFiles if (file.endswith('.wav'))]
    flacFiles = [path.splitext(file)[0] for file in allFiles if (file.endswith('.flac'))]
    return [file for file in wavFiles if file not in flacFiles]

config = configparser.ConfigParser()
config.read('extemporal.config')
dataDir = config.get('folders', 'data')
[convert(wavFile) for wavFile in filesToConvert()]

