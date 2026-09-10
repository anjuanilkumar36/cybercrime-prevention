def checktoxic():

    import nltk
    # nltk.download('punkt')
    # nltk.download('stopwords')
    from sklearn.model_selection import train_test_split

    path1 = "C:\\Users\\91815\\PycharmProjects\\myprivacy\\myapp\\cyberbullying-bdlstm.h5"
    path2 = "C:\\Users\\SHIBILA\\.PyCharm2017.1\\myapp\\tokenizer.json"

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import json

    import tensorflow as tf
    from tensorflow.keras.preprocessing.text import Tokenizer
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    from tensorflow.keras.callbacks import EarlyStopping

    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(2000, 64),  # embedding layer
        tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64, dropout=0.2, recurrent_dropout=0.2)),  # LSTM layer
        tf.keras.layers.Dropout(rate=0.2),  # dropout layer
        tf.keras.layers.Dense(64, activation='swish'),  # fully connected layer
        tf.keras.layers.Dense(1, activation='sigmoid')  # final layer
    ])

    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy', 'AUC'])
    model.load_weights(path1)

    import functools, re
    import random

    df = pd.read_csv("C:\\Users\\91815\\PycharmProjects\\myprivacy\\myapp\\static\\toxi.csv")
    df.cyberbullying_type.value_counts().plot.barh(xlim=(7800, 8000))

    stopwords = [i.lower() for i in nltk.corpus.stopwords.words('english') + [chr(i) for i in range(97, 123)]]
    x = df.tweet_text.apply(lambda text: re.sub("\s+", " ", ' '.join([i for i in re.sub("[^9A-Za-z ]", "",
                                                                                        re.sub("\\n", "",
                                                                                               re.sub("\s+", " ",
                                                                                                      re.sub(
                                                                                                          r'http\S+',
                                                                                                          '',
                                                                                                          text.lower())))).split(
        " ") if i not in stopwords]))).values.astype(str)

    y = df.cyberbullying_type != "not_cyberbullying"

    x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.4)
    x_val, x_test, y_val, y_test = train_test_split(x_val, y_val, test_size=0.25)

    tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=2000, oov_token="<OOV>")
    tokenizer.fit_on_texts(x)
    word_index = tokenizer.word_index

    x_test = ["hello"]

    x_test = pad_sequences(tokenizer.texts_to_sequences(x_test), maxlen=100, padding='post', truncating='post')
    y_pred = model.predict(x_test).round().T[0]

    print(y_pred)

    if y_pred[0] == 1.0:
        b = "normal"
        print(b)
    else:
        b = "toxic"
        print(b)
    return b

checktoxic()
