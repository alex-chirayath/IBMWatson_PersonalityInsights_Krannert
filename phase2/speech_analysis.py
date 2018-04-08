import requests
import json
import pprint
import csv
import sys

speech_to_text_url = 'https://stream.watsonplatform.net/speech-to-text/api/v1/recognize'
speech_to_text_username = 'be828bbc-2a8d-47e5-838b-ab79102d06c6'
speech_to_text_password = 'R5gsSmhsiIPv'

insights_url = 'https://gateway.watsonplatform.net/personality-insights/api/v2/profile?headers=true'
insights_username = '366bd94d-6871-482c-9ca9-84de1d1f0e6a'
insights_password = 'NlgUu6FjF7XF'

def getspeech(filename):
    """ Translate mp3 to json object with IBM Watson API.
    This module takes the name of a mp3 file, including the path to
    that file, and calls the IBM Watson speech-to-text api to
    get a json object describing the audio.
    Example json for audio 'Hello world':
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

    headers = {'Content-Type' : 'audio/mp3'}
    audio_file = open(filename, 'rb')
    params = {'model' : 'en-US_NarrowbandModel', 'speaker_labels' : 'true'}

    r = requests.post(speech_to_text_url, auth=(speech_to_text_username, speech_to_text_password), data=audio_file, headers=headers, params=params)

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
    # Key is speakerid, value is list of words associated with each speakerid
    speakers = {}

    interviewee = -1
    halfway_timestamp = speaker_data['speaker_labels'][len(speaker_data['speaker_labels']) - 1]['to']/2
    speaker_labels = list(speaker_data['speaker_labels'])

    # Separate speaker's words and add to speakers
    for item in speaker_data['results']:
        for words in item['alternatives']:
            for word in words['timestamps']:
                for label in speaker_labels:
                    if word[1] == label['from']:
                        if label['speaker'] in speakers.keys():
                            speakers[label['speaker']].append(word[0])
                        else:
                            speakers[label['speaker']] = [word[0]]

                        # Pick interviewee halfway through audio
                        if halfway_timestamp >= label['from'] and interviewee == -1:
                            interviewee = pickinterviewee(speakers)

                        break

    return speakers[interviewee]

def writelisttotxt(filename, list):
    text_file = open(filename, 'w')

    for item in list:
        text_file.write('%s\n' % item)

    text_file.close()

def getpersonalityinsights(filename):
    """ Get IBM Watson Personality Insights for file.
        Args:
            filename: string name of file to get personality insights from
        Returns:
            Response from IBM Watson Personality Insights API.
    """
    headers = {'Content-Type' : 'text/plain', 'Accept' : 'text/csv'}

    with open(filename, 'r') as myfile:
            data=myfile.read()

    r = requests.post(insights_url, auth=(insights_username, insights_password), data=data, headers=headers)

    return r

def speechanalysis(filename):
    """ Get Personality Profile from interview.
        Args:
            filename: string name of mp3 file to analyze
        Returns:
            void
    """
    # Get json response from speech-to-text API
    speaker_data = getspeech(filename)

    # Get list of words associated with interviewee
    interviewee_words = getintervieweewords(speaker_data)

    text_file_name = filename.replace('.mp3', '')  + '.txt'

    # Write interviewee's words to '<filename>.txt'
    writelisttotxt(text_file_name, interviewee_words)

    # Get response from Personality Insights API
    insights = getpersonalityinsights(text_file_name)

    csv_file_name = filename.replace('.mp3', '') + '.csv'

    # Write Personality Insights response to '<filename>.csv'
    with open(csv_file_name, 'w') as f:
        print >> f, insights.text

if __name__ == '__main__':
    speechanalysis(sys.argv[1])
