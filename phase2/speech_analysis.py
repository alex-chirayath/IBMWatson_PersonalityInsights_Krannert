import requests
import json
import pprint
import sys

url = "https://stream.watsonplatform.net/speech-to-text/api/v1/recognize"
username = "be828bbc-2a8d-47e5-838b-ab79102d06c6"
password = "R5gsSmhsiIPv"

def getjson(filename):
    """ Translate mp3 to json object with IBM Watson API.

    This module takes the name of a mp3 file, including the path to
    that file, and calls the IBM Watson speech-to-text api to
    get a json object describing the audio.

    Example json for audio "Hello world":
    {'result_index': 0,
        'results': [
            {
                'alternatives': [
                    {
                        'confidence': 0.872,
                        'timestamps':   [['hello', 0.03, 0.3],
                                        ['world', 0.3, 0.52],
                        'transcript': 'hello world'}],
                        'final': True
                ]
            }
        'speaker_labels': [
            {
                'confidence': 0.619,
                'final': False,
                'from': 0.03,
                'speaker': 1,
                'to': 0.3
            }, {
                'confidence': 0.619,
                'final': False,
                'from': 0.3,
                'speaker': 1,
                'to': 0.52}
        ]
    }

    Args:
        filename: String name of mp3 file, including the path to that file
    Returns:
        A json object containing audio transcription and speaker metadata
    """

    headers = {"Content-Type" : "audio/mp3"}
    audio_file = open(filename, "rb")
    params = {"model" : "en-US_NarrowbandModel", "speaker_labels" : "true"}

    r = requests.post(url, auth=(username, password), data=audio_file, headers=headers, params=params)

    return r.json()

def pickinterviewee(speaker):
    """ Choose which speaker is interviewee.

    Args:
        speaker: dictionary of speaker id to words spoken by that speaker
    Returns:
        An integer speaker id of person identified as interviewee
    """
    max_words = 0
    interviewee = -1

    for key, value in speaker.items():
        if len(value) > max_words:
            max_words = len(value)
            interviewee = key

    return interviewee

def getintervieweewords(speaker_data):
    """ Determine words spoken by interviewee.

    Args:
        speaker_data: json object containing mp3 metadata
    Returns:
        A list of strings that are the words spoken by the interviewee
    """
    speakers = {}
    interviewee = -1
    speaker_labels = list(speaker_data['speaker_labels'])

    for item in speaker_data['results']:
        for words in item['alternatives']:
            for word in words['timestamps']:
                for label in speaker_labels:
                    if word[1] == label['from']:
                        if label['speaker'] in speakers.keys():
                            speakers[label['speaker']].append(word[0])
                        else:
                            speakers[label['speaker']] = [word[0]]
                        break

    # TODO: change to checking for interviewee halfway through audio
    interviewee = pickinterviewee(speakers)

    return speakers[interviewee]

def writelisttotxt(filename, list):
    text_file = open(filename + ".txt", "w")

    for item in list:
        text_file.write("%s\n" % item)

    text_file.close()


def speechanalysis(filename):
    speaker_data = getjson(filename)

    json_data = open("data.txt").read()
    speaker_data = json.loads(json_data)

    interviewee_words = getintervieweewords(speaker_data)

    writelisttotxt(filename.replace(".mp3", ""), interviewee_words)

if __name__ == "__main__":
    speechanalysis(sys.argv[1])
