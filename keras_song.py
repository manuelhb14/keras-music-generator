import json
import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dropout, Dense, Activation, Embedding
import random
from selenium import webdriver
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def make_model(unique_chars):
    model = Sequential()
    
    model.add(Embedding(input_dim = unique_chars, output_dim = 512, batch_input_shape = (1, 1))) 
  
    model.add(LSTM(256, return_sequences = True, stateful = True))
    model.add(Dropout(0.2))
    
    model.add(LSTM(256, return_sequences = True, stateful = True))
    model.add(Dropout(0.2))
    
    model.add(LSTM(256, stateful = True)) 

    model.add((Dense(unique_chars)))
    model.add(Activation("softmax"))
    
    return model

def generate_sequence():
    epoch_num = np.random.choice([10, 20, 30, 40, 50, 60, 70, 80, 90])
    initial_index = (random.randint(5,43)) * 2
    seq_length = 1000
    with open(r'C:\Users\isabe\Documents\Music-Generation\Data2\char_to_index.json') as f:
        char_to_index = json.load(f)
    index_to_char = {i:ch for ch, i in char_to_index.items()}
    unique_chars = len(index_to_char)
    wpath = 'Weights_{}.h5'.format(epoch_num)
    model = make_model(unique_chars)
    model.load_weights(f'C:/Users/isabe/Documents/Music-Generation/Data2/Model_Weights/{wpath}')
     
    sequence_index = [initial_index]
    
    for _ in range(seq_length):
        batch = np.zeros((1, 1))
        batch[0, 0] = sequence_index[-1]
        predicted_probs = model.predict_on_batch(batch).ravel()
        sample = np.random.choice(range(unique_chars), size = 1, p = predicted_probs)
        sequence_index.append(sample[0])
    
    seq = ''.join(index_to_char[c] for c in sequence_index)
    cnt = 0
    for i in seq:
        cnt += 1
        if i == "\n":
            break
    seq1 = seq[cnt:]

    cnt = 0
    for i in seq1:
        cnt += 1
        if i == "\n" and seq1[cnt] == "\n":
            break
    seq2 = seq1[:cnt]
    print(seq2)
    return seq2

# music = generate_sequence()

def open_webbrowser():
    driver = webdriver.Chrome(executable_path='C:/Users/isabe/Downloads/chromedriver_win32/chromedriver.exe')
    driver.get("https://kickthejetengine.com/langorhythm/")
    button = driver.find_element_by_id('listen')
    textarea = driver.find_element_by_tag_name('textarea')
    textarea.send_keys(generate_sequence())
    button.click()
    