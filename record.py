import configparser, datetime, os, pyaudio, sys, threading, termios, wave, numpy

def record():
    numChannels = config.getint('audio', 'channels')
    sampleRate = config.getint('audio', 'samplerate')
    frameSize = config.getint('audio', 'framesize')
    print('recording...')
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format = pyaudio.paInt16,
        channels = numChannels,
        rate = sampleRate,
        input = True,
        frames_per_buffer = frameSize)
    frames = []
    while recording:
        data = stream.read(frameSize)
        frames.append(numpy.fromstring(data, numpy.int16))
    stream.stop_stream()
    stream.close()
    audio.terminate()
    frames = numpy.hstack(frames)
    print('finished recording')

    if len(frames) < sampleRate * 0.3:
        return
    trimSeconds = config.getfloat('audio', 'trimSeconds')
    trimSamples = int(sampleRate  * trimSeconds)
    frames = frames[trimSamples:] # trim begin
    frames = frames[:len(frames) - trimSamples] # trim end
    intMax = 32767
    frames *= int(32767 / max(abs(frames))) # normalize

    filename = datetime.datetime.now().isoformat() + '.wav'
    dataDir = config.get('folders', 'data')
    waveFile = wave.open(os.path.join(dataDir, filename), 'wb')
    waveFile.setnchannels(numChannels)
    waveFile.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    waveFile.setframerate(sampleRate)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    print("wrote", filename)

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
