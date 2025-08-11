# Imports
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np 
import pyaudio
import matplotlib.pyplot as plt 
from scipy.signal import stft 
import time

# ===== SPOTIFY AUTH =====
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="CLIENT_ID",
    client_secret="CLIENT_SCRT",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-read-currently-playing"
))

# ===== AUDIO CAPTURE SETTINGS =====
CHUNK = 1024              # Number of Audio samples per frame
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100              # Sampling Rate Hz

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# ===== MATPLOTLIB SETUP =====
plt.ion()
fig, ax = plt.subplots()

def plot_spectrogram(audio_data):
    f, t, Zxx = stft(audio_data, RATE, nperseg=256)
    ax.clear()
    ax.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
    ax.set_ylabel('Frequency [Hz]')
    ax.set_xlabel('Time [S]')
    plt.pause(0.01)

# ===== MAIN ROUTINE =====
print("Listening for audio... Press Ctrl+C to stop.")

try: 
    while True:
        # Get currently playing track
        current_track = sp.currently_playing()
        if current_track and current_track['is_playing']:
            song = current_track['item']['name']
            artist = current_track['item']['artists'][0]['name']
            print(f"Now playing: {song} - {artist}")

        # Read audio chunk from system
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_np = np.frombuffer(data, dtype=np.int16)

        # Plot spectrogram
        plot_spectrogram(audio_np)

        time.sleep(0.05)
except KeyboardInterrupt:
    print('\nStopping...')
    stream.stop_stream()
    stream.close()
    p.terminate()
