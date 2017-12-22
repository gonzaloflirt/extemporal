import configparser, datetime, os, pyaudio, sys, threading, termios, wave
from pydub import AudioSegment
from pydub import effects

def printDevices():
    audio = pyaudio.PyAudio()
    print('devices:')
    for i in range(0, audio.get_host_api_info_by_index(0).get('deviceCount')):
        device = audio.get_device_info_by_host_api_device_index(0, i)
        print('  ', i, device.get('name'),
                'ins:', device.get('maxInputChannels'),
                'outs:', device.get('maxOutputChannels'))
    deviceIndex = config.getint('audio', 'deviceIndex')
    print('using:', audio.get_device_info_by_host_api_device_index(0, deviceIndex).get('name'))

def record():
    numChannels = config.getint('audio', 'channels')
    sampleRate = config.getint('audio', 'samplerate')
    frameSize = config.getint('audio', 'framesize')
    deviceIndex = config.getint('audio', 'deviceIndex')
    print('recording...')
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format = pyaudio.paInt16,
        channels = numChannels,
        rate = sampleRate,
        input = True,
        frames_per_buffer = frameSize,
        input_device_index = deviceIndex)

    frames = AudioSegment.empty()
    while recording:
        frames += AudioSegment(
            stream.read(frameSize), sample_width=2, frame_rate = sampleRate, channels=1)
    stream.stop_stream()
    stream.close()
    audio.terminate()
    print('finished recording')

    trim = config.getfloat('audio', 'trimSeconds') * 1000
    treshold = config.getfloat('audio', 'compressorTreshold')
    ratio = config.getfloat('audio', 'compressorRatio')
    attack = config.getfloat('audio', 'compressorAttack')
    release = config.getfloat('audio', 'compressorRelease')
    frames = frames[trim:] # trim begin
    frames = frames[:-trim] # trim end
    frames = effects.compress_dynamic_range(
        frames, threshold = treshold, ratio = ratio, attack = attack, release = release)
    frames = effects.normalize(frames) # normalize

    if (frames.duration_seconds > 0):
        filename = datetime.datetime.now().isoformat()
        dataDir = config.get('folders', 'data')
        frames.export(os.path.join(dataDir, filename) + '.wav', format = 'wav')
        frames.set_frame_rate(16000).export(os.path.join(dataDir, filename) + '.flac', format = 'flac')
        print("wrote", filename, 'duration:', frames.duration_seconds, 'seconds')

def waitForKeypress():
    fd = sys.stdin.fileno()
    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)
    try:
        result = sys.stdin.read(1)
    except IOError:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    return result

config = configparser.ConfigParser()
config.read('extemporal.config')
printDevices()
recording = False
while True:
    key = waitForKeypress()
    if key == 'r' and not recording:
        recording = True
        threading.Thread(target=record).start()
    else:
        recording = False
        if key == 'q':
            break
