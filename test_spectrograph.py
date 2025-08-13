# Imports
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np 
import pyaudio
import matplotlib.pyplot as plt 
from scipy.signal import stft 
import time

import sptify_config

print("[INFO] Starting program...")

# ===== SPOTIFY AUTH =====
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=sptify_config.SPTIFY_CLIENT_ID,
    client_secret=sptify_config.SPTIFY_CLIENT_SECRET,
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
# For FFT
line, = ax.plot([], [], lw=2)
ax.set_xlim(0, 22050)  # Nyquist freq (half of 44100)
ax.set_ylim(0, 10000)  # Adjust based on expected amplitude
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Amplitude")
ax.set_title("Live FFT Frequency Spectrum")
ax.grid(True)

def plot_spectrogram(audio_data):
    f, t, Zxx = stft(audio_data, RATE, nperseg=256)
    ax.clear()
    ax.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
    ax.set_ylabel('Frequency [Hz]')
    ax.set_xlabel('Time [S]')
    plt.pause(0.01)

def plot_fft(signal, sample_rate):
    """
    Plots a single FFT frame for the given audio signal.
    
    Parameters:
        signal (np.ndarray): 1D array of audio samples.
        sample_rate (int): Sampling rate in Hz.
    """
    # Mono conversion if needed
    if signal.ndim > 1:
        signal = signal.mean(axis=1)

    # Apply FFT
    fft_result = np.fft.fft(signal)
    fft_magnitude = np.abs(fft_result)  # Magnitude spectrum

    # Only keep the positive frequencies
    freqs = np.fft.fftfreq(len(signal), 1/sample_rate)
    mask = freqs >= 0
    freqs = freqs[mask]
    fft_magnitude = fft_magnitude[mask]

    # Plot
    line.set_data(freqs, fft_magnitude)
    ax.set_ylim(0, max(fft_magnitude)*1.1)  # auto-scale y axis

    fig.canvas.draw()
    fig.canvas.flush_events()


# ===== MAIN ROUTINE =====
print("Listening for audio... Press Ctrl+C to stop.")

try: 
    while True:
    # for i in range(20):
        # Get currently playing track
        print("[INFO] Getting current track")
        current_track = sp.currently_playing()

        # print(f"[INFO] Current Track: {current_track}")
        if current_track and current_track['is_playing']:
            song = current_track['item']['name']
            artist = current_track['item']['artists'][0]['name']
            print(f"Now playing: {song} - {artist}")

        # Read audio chunk from system
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_np = np.frombuffer(data, dtype=np.int16)
        # If stereo, convert to mono by averaging channels
        if CHANNELS == 2:
            audio_np = audio_np.reshape(-1, 2)
            audio_np = audio_np.mean(axis=1)

        # Plot spectrogram
        # plot_spectrogram(audio_np)
        # Plot FFT
        plot_fft(audio_np, RATE)

        time.sleep(0.05)
except KeyboardInterrupt:
    print('\nStopping...')
    stream.stop_stream()
    stream.close()
    p.terminate()

print("[INFO] Program complete.")