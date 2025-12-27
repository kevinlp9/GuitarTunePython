import numpy as np
from scipy.signal import butter, lfilter

class SignalProcessor:
    def __init__(self, rate):
        self.rate = rate

    def fft(self, data):
        return np.fft.rfft(data)

    def dominant_freq(self, data, min_freq=70.0, max_freq=350.0):
        frequencies = np.fft.rfftfreq(len(data), 1.0 / self.rate)
        magnitude = np.abs(self.fft(data))
        relevant_indices = np.where((frequencies >= min_freq) & (frequencies <= max_freq))
        relevant_frequencies = frequencies[relevant_indices]
        relevant_magnitudes = magnitude[relevant_indices]
        if len(relevant_frequencies) > 0:
            dominant_index = np.argmax(relevant_magnitudes)
            dominant_freq = relevant_frequencies[dominant_index]
            dominant_magnitude = relevant_magnitudes[dominant_index]
            return dominant_freq, dominant_magnitude
        else:
            return None, None

    def butter_lowpass(self, cutoff, order=5):
        nyquist = 0.5 * self.rate
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def lowpass_filter(self, data, cutoff, order=5):
        b, a = self.butter_lowpass(cutoff, order=order)
        y = lfilter(b, a, data)
        return y

