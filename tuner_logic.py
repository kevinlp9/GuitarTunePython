class TunerLogic:
    def __init__(self, reference_frequencies, tolerance=1.0):
        self.reference_frequencies = reference_frequencies
        self.tolerance = tolerance

    def find_closest_string(self, frequency):
        closest_string = None
        min_distance = float('inf')
        for string, ref_freq in self.reference_frequencies.items():
            distance = abs(frequency - ref_freq)
            if distance < min_distance:
                min_distance = distance
                closest_string = string
        return closest_string, min_distance

