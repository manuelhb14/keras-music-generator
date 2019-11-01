# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 08:46:28 2019

@author: isabe
"""
from flask import Flask
from flask_ask import Ask, statement, question
from microphone import record_audio
from trainedNetwork import model
import numpy as np
import urllib.request
import urllib.parse
import re
import urllib.request
import urllib.parse
import youtube_dl
import librosa

#To initialize app and flask functions
app = Flask(__name__)
ask = Ask(app, '/')

@app.route('/')
def homepage():
    return "Hello"

#Elementary functions
@ask.launch
def start_skill():      #Welcome for user
    welcome_message = 'Hello there, what would you like me to do? You can say, Alexa search for this song, or, Alexa listen to this song, and i will tell you the genre'
    return question(welcome_message)

def process_audio(y, sr=44100):         #Extract characteristics
    rmse = librosa.feature.rmse(y=y)
    chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
    spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    zcr = librosa.feature.zero_crossing_rate(y)
    mfcc = librosa.feature.mfcc(y=y, sr=sr)
    to_append = f'{np.mean(chroma_stft)} {np.mean(rmse)} {np.mean(spec_cent)} {np.mean(spec_bw)} {np.mean(rolloff)} {np.mean(zcr)}'
    for e in mfcc:
        to_append += f' {np.mean(e)}'
    song = np.array([float(x) for x in to_append.split()])
    return np.reshape(song, (1,26))
  
def genre_index(pred):    #List of 12 with predictions of each genre
    pred = np.argmax(pred)
    if pred == 0:
       return 'blues'
    elif pred == 1:
       return 'classical'
    elif pred == 2:
       return 'country'
    elif pred == 3:
       return 'disco'
    elif pred == 4:
       return 'hiphop'
    elif pred == 5:
       return 'jazz'
    elif pred == 6:
       return 'metal'
    elif pred == 7:
       return 'pop'
    elif pred == 8:
       return 'reggae'
    elif pred == 9:
       return 'rock'
    elif pred == 10:
       return 'latin'
    elif pred == 11:
       return 'electronic'
    else:
       return 'Sorry, a problem has occurred'
  
#def record_audio():
#    listen_time = 5  # seconds
#    frames, sr = record_audio(listen_time)
#    y = np.hstack([np.frombuffer(i, np.int16) for i in frames]).astype(float)  
#    return y

def get_url(songname):
    query_string = urllib.parse.urlencode({"search_query" : songname})
    html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
    return "http://www.youtube.com/watch?v=" + search_results[0]

def download(url, filename):
    ydl_opts = {'outtmpl': f'audio_alexa/{filename}',
                'format': 'bestaudio/best',
                'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192'}]}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    
@ask.intent("ListenIntent")
def listen_to_song():
    return statement("Listen ran")

@ask.intent("SearchIntent")
def search_song(Query):
    songname = Query
    filename = (Query + '.mp3').replace(' ', '')
    url = get_url(songname)
    download(url, filename)
    return statement('{} is now saved on your computer'.format(str(Query)))

@ask.intent("CancelIntent")
def share_coin_result():
    return statement('Okay, goodbye')

if __name__ == '__main__':
    app.run(debug=True)