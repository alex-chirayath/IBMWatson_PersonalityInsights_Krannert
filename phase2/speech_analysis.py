import requests
import json

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
        json: json object containing audio transcription and speaker metadata
    """

    headers = {"Content-Type" : "audio/mp3"}
    audio_file = open(filename, "rb")
    params = {"model" : "en-US_NarrowbandModel", "speaker_labels" : "true"}

    r = requests.post(url, auth=(username, password), data=audio_file, headers=headers, params=params)

    return r.json()

def speechanalysis(filename):
    speaker_data = getjson(filename)

if __name__ == "__main__":
    speechanalysis(sys.argv[1])
