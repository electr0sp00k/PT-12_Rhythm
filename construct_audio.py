import csv
from scipy.io import wavfile
import numpy as np
import librosa

def pitch_shift(data, samplerate, semitones):
    '''Shift the pitch of the waveform.'''
    return librosa.effects.pitch_shift(data, n_steps=semitones, sr=samplerate)

def adjust_volume(data, volume):
    '''Adjust the volume of a waveform.'''
    return data * (volume / 100.0)

def construct_audio(csv_path, output_path):
    '''Constructs the waveform based on the specified pattern provided.'''
    with open(csv_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        # First line: BPM
        bpm = int(next(reader)[0])

        # Find the longest sequence in CSV 
        total_steps = max(len(row[4:]) for row in reader)

        print(f"total steps: {total_steps}")

        # Reset reader to beginning
        csv_file.seek(0)
        next(reader)

        #Define output sample rate
        output_samplerate = 41000

        # Calculate duration of each step in seconds, samples
        step_duration = 60.0 / bpm
        step_duration_samples = int(step_duration * output_samplerate)
        total_duration_samples = int(step_duration_samples * total_steps)

        # Initialize an empty list to store each track
        tracks = []

        # Process each sample line
        for row in reader:
            wav_file, volume, pitch, step_multiplier, *steps = row

            # Defaults for volume and pitch
            volume = int(volume) if volume else 100
            pitch = int(pitch) if pitch else 0
            step_multiplier = max(1, min(8, int(step_multiplier) if step_multiplier else 1))

            steps = [max(0, bool(int(x))) if x else 0 for x in steps]
            
            # Read sample, convert to mono and float
            samplerate, data = wavfile.read(f"samples/{wav_file}")
            if data.ndim == 2:
                data = data.mean(axis=1)

            data = data.astype(np.float32)
            
            # Handle for a variety of sample rates by resampling as 41000
            data = librosa.resample(data, orig_sr=samplerate, target_sr=output_samplerate)
            sample_length = len(data)
            
            # Pitch shift and volume
            data = pitch_shift(data, output_samplerate, pitch)
            data = adjust_volume(data, volume)


            # Create an empty array for this track
            track_data = np.zeros(total_duration_samples)
            
            # Length of step during step multiply
            sub_step_samples = step_duration_samples // step_multiplier
            
            for i, step in enumerate(steps):
                if int(step):
                    for n in range(step_multiplier):
                        start = i * step_duration_samples + n * sub_step_samples
                        end = min(start + sample_length, total_duration_samples)
                        track_data[start:end] = data[:(end - start)]
                    
            tracks.append({'data': track_data, 'steps': steps})
            
        # Create buffer for final output
        output_data = np.zeros(total_duration_samples)
        
        for track in tracks:
            output_data[:len(track['data'])] += track['data']
            
        # Prevent Clipping
        output_data = np.clip(output_data, -32768, 32767).astype(np.int16)
        
        wavfile.write(output_path, output_samplerate, output_data)

csv_path = 'pattern.csv'
output_path = 'output.wav'
construct_audio(csv_path, output_path)