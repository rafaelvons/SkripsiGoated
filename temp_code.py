# overview figure of data distribution

import matplotlib.pyplot as plt
import seaborn as sns
import os

directory = "donateacry-corpus-master/donateacry_corpus_cleaned_and_updated_data/"
cry_reasons = next(os.walk(directory))[1]

label_list = []
data_list = []

for folder in cry_reasons:
    label_data = (folder, len(next(os.walk(directory+folder))[2]))
    label = (label_data[0])
    data = (label_data[1])
    label_list.append(label)
    data_list.append(data)

colors = sns.color_palette('pastel')[0:5]

#create pie chart
plt.pie(data_list, labels = label_list, colors = colors, autopct='%.0f%%', shadow=True)
plt.title("Dataset feature distribution (%)")
plt.show()
import wave
wav_obj = wave.open('donateacry-corpus-master/donateacry_corpus_cleaned_and_updated_data/belly_pain/549a46d8-9c84-430e-ade8-97eae2bef787-1430130772174-1.7-m-48-bp.wav', 'rb')

# sampling frequency (no. of samples per second)
sample_freq = wav_obj.getframerate()
sample_freq
# number of individual samples
n_samples = wav_obj.getnframes()
n_samples
# duration of audio file (in seconds)
t_audio = n_samples/sample_freq
t_audio
# check if file was recorded in mono or stereo
n_channels = wav_obj.getnchannels()
n_channels # mono
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display

import glob
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm
# Plot an example file
sample_file = "belly_pain/549a46d8-9c84-430e-ade8-97eae2bef787-1430130772174-1.7-m-48-bp.wav"
fname = directory + sample_file
samples, sample_rate = librosa.load(fname)
max_time = samples.size / sample_rate
time_axis = np.linspace(0, max_time, samples.size)

fig, ax1 = plt.subplots(1, figsize=(15, 3))
ax1.plot(time_axis, samples)
ax1.set_xlim([time_axis.min(), time_axis.max()])
ax1.set_ylabel("Amplitude")
ax1.set_xlabel("Time [s]")
ax1.set_title("Raw audio")
S = librosa.feature.melspectrogram(y=samples, sr=sample_rate)
fig, ax = plt.subplots(1, 2, figsize=(15, 5))
img = librosa.display.specshow(librosa.amplitude_to_db(S,ref=np.max), y_axis='log',sr=sample_rate, x_axis='time', ax=ax[0])
ax[0].set_title('Log Amplitude')
fig.colorbar(img, ax=ax[0], format="%+2.0f dB")
img = librosa.display.specshow(librosa.power_to_db(S,ref=np.max), y_axis='log',sr=sample_rate, x_axis='time', ax=ax[1])
ax[1].set_title('Log Power')
fig.colorbar(img, ax=ax[1], format="%+2.0f dB")
plt.show()
# 1) Load audio samples:
labels = ['belly_pain', 'burping', 'discomfort', 'hungry', 'tired']
dataset_power_scaled = {k: [] for k in labels}

for k in labels:
    print("Loading and preprocessing {} data".format(k))
    files = glob.glob(directory + "{}/*".format(k))
    for fname in tqdm(files):
        samples, sample_rate = librosa.load(fname)
        S = librosa.feature.melspectrogram(y=samples, sr=sample_rate)
        scaler = MinMaxScaler()
        dataset_power_scaled[k].append(scaler.fit_transform(librosa.power_to_db(S, ref=np.max)).flatten())
# 2) build a usable dataset: using the dataset as is

# 2.1) concatenate dataset
total_samples = np.sum([len(x) for x in dataset_power_scaled.values()])
concatenated_data = np.zeros((40000, total_samples))  # choose 40k features to cover all data lengths in the dataset (will be zero-padded)
label_sequence = []
ctr = 0
for k, v in dataset_power_scaled.items():
    for sample in v:
        label_sequence.append(k)
        concatenated_data[:sample.shape[0], ctr] = sample
        ctr += 1

# 2.2) create labels (one-hot encoded)
y = np.zeros((np.unique(label_sequence).shape[0], total_samples))
for idx, lab in enumerate(label_sequence):
    y[np.where(lab == np.unique(label_sequence))[0][0], idx] = 1.

# 2.3) randomize samples (because they were read from the dictionary they are ordered by label)
indices = np.random.permutation(total_samples)
X = concatenated_data[:, indices]
label_sequence = np.array(label_sequence)[indices]
y = y[:, indices]
# 3) build a (control) usable dataset: using permutations of the dictionary elements 

# a) how many total samples to we have? 
total_samples = np.sum([len(x) for x in dataset_power_scaled.values()])

# b) create a random sequence
label_sequence_control = np.random.choice(labels, size=total_samples)

# c) sample dataset
X_control = np.zeros((40000, total_samples))
for idx, k in enumerate(label_sequence_control):
    smp = np.random.choice(dataset_power_scaled[k], 1)[0]
    X_control[:smp.shape[0], idx] = smp

# d) create labels (one-hot encoded)
y_control = np.zeros((np.unique(label_sequence_control).shape[0], total_samples))
for idx, lab in enumerate(label_sequence_control):
    y_control[np.where(lab == np.unique(label_sequence_control))[0][0], idx] = 1.
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X.T, y.T, test_size=0.25)
X_train_control, X_test_control, y_train_control, y_test_control = train_test_split(X_control.T, y_control.T, test_size=0.25)
# Representation of a melspectrogram for one random sample

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

fname = 'donateacry-corpus-master/donateacry_corpus_cleaned_and_updated_data/belly_pain/549a46d8-9c84-430e-ade8-97eae2bef787-1430130772174-1.7-m-48-bp.wav'
samples, sample_rate = librosa.load(fname)

fig = plt.figure(figsize=[7,5])
ax = fig.add_subplot(111)
ax.axes.get_xaxis().set_visible(False)
ax.axes.get_yaxis().set_visible(False)
plt.title('Melspectrogram for 549a46d8-9c84-430e-ade8-97eae2bef787-1430130772174-1.7-m-48-bp.wav')
S = librosa.feature.melspectrogram(y=samples, sr=sample_rate)
librosa.display.specshow(librosa.power_to_db(S, ref=np.max))
from sklearn.neural_network import MLPClassifier
clf1 = MLPClassifier(activation="tanh", solver="adam", alpha=1e-3, learning_rate="adaptive", random_state=1, max_iter=300)
clf1.fit(X_train, y_train)
clf1.score(X_test, y_test)
'''import optuna
from joblib import parallel_backend

def objective(trial):
    n_layers = trial.suggest_int('n_layers', 1, 4)
    layers = []
    for i in range(n_layers):
        layers.append(trial.suggest_int(f'n_units_{i}', 1, 1000, log=True))

    hyperparameters = {
        'hidden_layer_sizes': tuple(layers),
        'activation': trial.suggest_categorical("activation", ['identity', 'logistic', 'tanh', 'relu']),
        'solver': trial.suggest_categorical("solver", ['lbfgs', 'sgd', 'adam']),
        'alpha': trial.suggest_float("alpha", 1e-5, 1., log=True),
        'learning_rate': trial.suggest_categorical("learning_rate", ['constant', 'invscaling', 'adaptive'])
    }
    with parallel_backend('threading', n_jobs=32):
        clf = MLPClassifier(**hyperparameters, max_iter=1000)
        clf.fit(X_train, y_train)
        score = clf.score(X_test, y_test)
    return score

study_name = "MLP_optune2"  # Unique identifier of the study.
storage_name = "sqlite:///{}.db".format(study_name)
study = optuna.create_study(study_name=study_name, storage=storage_name, direction="maximize", load_if_exists=True)
study.optimize(objective, n_trials=100)'''
import optuna

study_name = "MLP_optune2"  
storage_name = "sqlite:///{}.db".format(study_name)
loaded_study_clf1 = optuna.load_study(study_name=study_name, storage=storage_name)
print("Best result:")
loaded_study_clf1.best_params, loaded_study_clf1.best_value
clf1_best_params = loaded_study_clf1.best_params
clf1_best_params = loaded_study_clf1.best_params
clf1_best_params.update({'hidden_layer_sizes': (4, 4, 11, 4, 1)})
clf1_best_params.pop("n_layers")
clf1_best_params.pop("n_units_0")
clf1_best_params.pop("n_units_1")
clf1_best_params.pop("n_units_2")
clf1_best_params.pop("n_units_3")
fig = optuna.visualization.matplotlib.plot_optimization_history(loaded_study_clf1)
study_name = "MLP_optune"  # Control study (balanced classes)
storage_name = "sqlite:///{}.db".format(study_name)
loaded_study_clf1_control = optuna.load_study(study_name=study_name, storage=storage_name)
print("Best result:")
loaded_study_clf1_control.best_params, loaded_study_clf1_control.best_value
clf1_best_params_control = loaded_study_clf1_control.best_params
clf1_best_params_control.update({'hidden_layer_sizes': (369, 10)})
clf1_best_params_control.pop("n_layers")
clf1_best_params_control.pop("n_units_0")
clf1_best_params_control.pop("n_units_1")
fig = optuna.visualization.matplotlib.plot_optimization_history(loaded_study_clf1_control)
clf1 = MLPClassifier(max_iter=1000, **clf1_best_params)
clf1.fit(X_train, y_train)
fig, ax = plt.subplots()
ax.plot(clf1.loss_curve_)
ax.set_xlabel("Epoch")
ax.set_ylabel("Log-loss")

print("Test_accuracy:")
clf1.score(X_test, y_test)
clf1_control = MLPClassifier(max_iter=1000, **clf1_best_params_control)
clf1_control.fit(X_train_control, y_train_control)
from sklearn.svm import SVC
clf2 = SVC(C=1e-5, kernel="sigmoid")
clf2.fit(X_train, np.argmax(y_train, 1))
clf2.score(X_test, np.argmax(y_test, 1))
"""import optuna
from joblib import parallel_backend

def objective(trial):

    hyperparameters = {
        'C': trial.suggest_float("C", 1e-5, 1.0, log=True),
        'kernel': trial.suggest_categorical("kernel", ['linear', 'poly', 'rbf', 'sigmoid']),}

    with parallel_backend('threading', n_jobs=32):
        clf = SVC(**hyperparameters)
        clf.fit(X_train, np.argmax(y_train, 1))
        score = clf.score(X_test, np.argmax(y_test, 1))
    return score

study_name = "SVC_optune2"  # Unique identifier of the study.
storage_name = "sqlite:///{}.db".format(study_name)
study = optuna.create_study(study_name=study_name, storage=storage_name, direction="maximize")
study.optimize(objective, n_trials=100)"""
study_name = "SVC_optune2"  # Unique identifier of the study.
storage_name = "sqlite:///{}.db".format(study_name)
loaded_study_clf2 = optuna.load_study(study_name=study_name, storage=storage_name)
print("Best result:")
loaded_study_clf2.best_params, loaded_study_clf2.best_value
clf2_best_params = loaded_study_clf2.best_params
study_name = "SVC_optune"  # control dataset
storage_name = "sqlite:///{}.db".format(study_name)
loaded_study_clf2_control = optuna.load_study(study_name=study_name, storage=storage_name)
print("Best result:")
loaded_study_clf2_control.best_params, loaded_study_clf2_control.best_value
clf2_best_params_control = loaded_study_clf2_control.best_params
clf2 = SVC(**clf2_best_params)
clf2.fit(X_train, np.argmax(y_train, 1))
print("Test_accuracy:")
clf2.score(X_test, np.argmax(y_test, 1))
clf2_control = SVC(**clf2_best_params_control)
clf2_control.fit(X_train_control, np.argmax(y_train_control, 1))
print("Test_accuracy:")
clf2_control.score(X_test_control, np.argmax(y_test_control, 1))
import pandas as pd
accuracies = {
    "MLP": [clf1.score(X_test, y_test)],
    "MLP_control": [clf1_control.score(X_test_control, y_test_control)],
    "SVM": [clf2.score(X_test, np.argmax(y_test, 1))],
    "SVM_control": [clf2_control.score(X_test_control, np.argmax(y_test_control, 1))]
}
acc = pd.DataFrame(accuracies)
acc
acc.T.plot.bar()
fname = "sample1.wav"
samples, sample_rate = librosa.load(fname)
S = librosa.feature.melspectrogram(y=samples, sr=sample_rate)
fig, ax = plt.subplots(1, 2, figsize=(15, 5))
img = librosa.display.specshow(librosa.amplitude_to_db(S,ref=np.max), y_axis='log',sr=sample_rate, x_axis='time', ax=ax[0])
ax[0].set_title('Log Amplitude')
fig.colorbar(img, ax=ax[0], format="%+2.0f dB")
img = librosa.display.specshow(librosa.power_to_db(S,ref=np.max), y_axis='log',sr=sample_rate, x_axis='time', ax=ax[1])
ax[1].set_title('Log Power')
fig.colorbar(img, ax=ax[1], format="%+2.0f dB")
plt.show()
new_data = librosa.amplitude_to_db(S, ref=np.max).flatten()
scaler = MinMaxScaler()
new_data_scaled = scaler.fit_transform(librosa.amplitude_to_db(S, ref=np.max)).flatten()

np.array([new_data_scaled]).shape
dd = np.zeros((40000, 1))
if new_data_scaled.shape[0] < 40000:
    dd[:new_data_scaled.shape[0], 0] = new_data_scaled
else:
    dd[:, 0] = new_data_scaled[:40000]
clf1.predict(dd.T)
clf1_control.predict(dd.T)
clf2.predict(dd.T)
clf2_control.predict(dd.T)
