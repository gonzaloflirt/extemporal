import configparser, pickle
from os import listdir, path

def readResponseFile(responseFile):
    with open (path.join(dataDir, responseFile + '.resp'), 'rb') as file:
        responses = pickle.load(file)
    for lang in responses:
        for result in responses[lang].results:
            alternative = result.alternatives[0]
            confidence = alternative.confidence
            for word_info in alternative.words:
                word = word_info.word.replace('\'', '\\\'') \
                    .lower().encode('ascii', 'ignore').decode('utf-8')
                start = word_info.start_time.seconds + word_info.start_time.nanos * 1e-9
                end = word_info.end_time.seconds + word_info.end_time.nanos * 1e-9
                length = end - start
                scString = '(\'word\': \'' + word
                scString += '\', \'start\': ' + str(start)
                scString += ', \'length\': ' + str(length)
                scString += ', \'confidence\':' + str(confidence)
                scString += ', \'language\': \''  + lang
                scString += '\', \'file\': \'' + responseFile + '.wav\')'
                scStrings.append(scString)

def responseFiles():
    allFiles = [file for file in listdir(dataDir) if (path.isfile(path.join(dataDir, file)))]
    return [path.splitext(file)[0] for file in allFiles if (file.endswith('.resp'))]

config = configparser.ConfigParser()
config.read('extemporal.config')
dataDir = config.get('folders', 'data')

scStrings = []
[readResponseFile(responseFile) for responseFile in responseFiles()]
outFile = open(path.join(dataDir, config.get('folders', 'scFile')), 'w')
outFile.write('[' + ',\n'.join(event for event in scStrings) + ']')
outFile.close()
