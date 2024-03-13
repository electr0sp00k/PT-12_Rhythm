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
        # Calculate duration of each step in seconds
        step_duration = 60.0 / bpm

        # Initialize an empty list to store each track
        tracks = []

        # Process each sample line
        for row in reader:
            wav_file, volume, pitch, *steps = row

            # Defaults for volume and pitch
            try:
                volume = int(row[1]) if row[1] else 100
            except ValueError:
                pass
            
            try:
                pitch = int(row[2]) if row[2] else 0
            except ValueError:
                pass

            steps = [bool(int(x)) for x in steps]
            
            # Read sample, convert to mono and float
            samplerate, data = wavfile.read(f"samples/{wav_file}")
            if data.ndim == 2:
                data = data.mean(axis=1)

            data = data.astype(np.float32)
            
            # Handle for a variety of sample rates by resampling as 41000
            output_samplerate = 41000
            data = librosa.resample(data, orig_sr=samplerate, target_sr=output_samplerate)
            
            data = pitch_shift(data, output_samplerate, pitch)
            data = adjust_volume(data, volume)
            
            # Calculate the total duration based on the longest pattern
            total_steps = max(len(steps), max(len(track['steps']) for track in tracks) if tracks else 0)
            total_duration = step_duration * total_steps
            
            # Create an empty array for this track
            track_data = np.zeros(int(total_duration * output_samplerate))
            
            for i, on_this_beat in enumerate(steps):
                if on_this_beat:
                    start = int(i * step_duration * output_samplerate)
                    end = start + len(data)
                    track_data[start:end] += data[:len(track_data[start:end])]
                    
            tracks.append({'data': track_data, 'steps': steps})
            
        # Take the longest track as the base
        output_data = np.zeros_like(max(tracks, key=lambda x: len(x['data']))['data'])
        
        for track in tracks:
            output_data[:len(track['data'])] += track['data']
            
        # Prevent Clipping
        output_data = np.clip(output_data, -32768, 32767).astype(np.int16)
        
        wavfile.write(output_path, output_samplerate, output_data)

csv_path = 'pattern.csv'
output_path = 'output.wav'
construct_audio(csv_path, output_path)