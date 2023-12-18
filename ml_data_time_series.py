# -*- coding: utf-8 -*-
"""ML_Data-Time-Series.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1x-0GfRLj63puZWJ6AGo39mjsDt9I5Hxa

# Proyek Kedua : Membuat Model Machine Learning dengan Data Time Series

Nama Lengkap : Muhammad Fadhil Abyansyah

Username : fadhil-abyansyah

Email : infofadhil29@gmail.com


---
"""

# Import library
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from keras.layers import Dense, LSTM
from sklearn.model_selection import train_test_split

# Membaca file CSV
df = pd.read_csv('delhi-weather.csv')
df.head()

# Menampilkan jumlah kolom dan baris
df.shape

# Menampilkan jumlah baris dan kolom, nama kolom dan tipe data, dan jumlah nilai non-null
df.info()

# Menghitung jumlah nilai null dalam setiap kolom dari DataFrame
df.isnull().sum()

# Mengubah kolom 'datetime_utc' menjadi tipe data datetime dan menampilkan lima baris pertama:
df['datetime_utc']=pd.to_datetime(df['datetime_utc'])
df['datetime_utc'].head()

# Mengisi nilai null dalam kolom ' _tempm' dengan rata-rata dan mengganti nilai DataFrame dengan hanya dua kolom ('datetime_utc' dan ' _tempm'):
df[' _tempm'].fillna(df[' _tempm'].mean(), inplace=True)
df = df[['datetime_utc',' _tempm' ]]
df.head()

# Mengubah kolom datatime_utc menjadi date
delhi=df[['datetime_utc',' _tempm']].copy()
delhi['date'] = delhi['datetime_utc'].dt.date

# Membuat df baru bernama delhinew
delhinew=delhi.drop('datetime_utc',axis=1)
delhinew.set_index('date', inplace= True)
delhinew.head()

# Menampilkan jumlah baris dan kolom, nama kolom dan tipe data, dan jumlah nilai non-null dari delhinew
delhinew.info()

# Membuat plot dari data delhi weather
date = delhi['date'].values
temp = delhi[' _tempm'].values

plt.figure(figsize=(18,6))
plt.plot(delhinew)
plt.title('Delhi Weather')
plt.xlabel('Date')
plt.ylabel('Temperature')
plt.show()

# Menerima sebuah atribut yg telah dikonversi menjadi tipe numpy,lalu mengembalikan label dan atribut dari dataset dalam bentuk batch
def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

# Split data dimana validation setnya 20% dari dataset
x_train, x_test, y_train, y_test = train_test_split(temp, date, test_size = 0.2, random_state = 0 , shuffle=False)

# Mengetahui ukuran x_train dan x_test
print(len(x_train), len(x_test))

# Model
data_x_train = windowed_dataset(x_train, window_size=60, batch_size=100, shuffle_buffer=5000)
data_x_test = windowed_dataset(x_test, window_size=60, batch_size=100, shuffle_buffer=5000)

model = tf.keras.models.Sequential([
  tf.keras.layers.LSTM(64, return_sequences=True),
  tf.keras.layers.Dense(30, activation="relu"),
  tf.keras.layers.Dense(1),
  tf.keras.layers.Lambda(lambda x: x * 400)
])

# Optimizer menggunakan Learning Rate
lr_schedule = tf.keras.callbacks.LearningRateScheduler(
    lambda epoch: 1e-8 * 10**(epoch / 20))
optimizer = tf.keras.optimizers.SGD(learning_rate=1e-8, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])

# Melihat nilai maksimum dan minimum dari kolom '_tempm' dalam DataFrame
max = df[' _tempm'].max()
print('Max value: ' )
print(max)
min = df[' _tempm'].min()
print('Min Value: ')
print(min)

# Menghitung range data (10% dari range) dan menyimpannya dalam variabel x
x = (max - min) * (10 / 100)
print(x)

# Callback untuk menghentikan pelatihan model jika MAE (Mean Absolute Error) < 10% dari skala data
class CallBack(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('mae')< x):
      self.model.stop_training = True
      print('\nUntuk Epoch', epoch, ' pelatihan dihentikan.''\nKarena MAE dari model telah mencapai < 10% dari skala data')
callbacks = CallBack()

# Melakukan pelatihan model dengan data pelatihan dan data validasi
tf.keras.backend.set_floatx('float64')
history = model.fit(data_x_train,
                    epochs=100,
                    validation_data=data_x_test,
                    callbacks=[callbacks])

# Menampilkan plot untuk MAE
plt.plot(history.history['mae'])
plt.plot(history.history['val_mae'])
plt.title('MAE')
plt.ylabel('MAE')
plt.xlabel('Epoch')
plt.legend(['train', 'test'], loc='upper right')
plt.show()

# Menampilkan plot untuk loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['train', 'test'], loc='upper right')
plt.show()