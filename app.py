from flask import Flask, render_template, request, jsonify, url_for
import os
from construct_audio import construct_audio

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Returns the list of wav files in the samples directory
@app.route('/list_samples')
def list_samples():
    samples_directory = 'samples'
    try:
        files = os.listdir(samples_directory)
        # Filter out non-WAV files
        wav_files = [file for file in files if file.endswith('.wav')]
        return jsonify(wav_files)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/update_csv', methods=['POST'])
def update_csv():

    # Grab BPM as single value
    bpm = request.form['bpm']

    # Grab samples, volume, and pitch lists for each submitted sequence
    samples = request.form.getlist('samples[]')
    volumes = request.form.getlist('volume[]')
    pitches = request.form.getlist('pitch[]')

    print(f"Samples:{samples}")
    print(f"volume:{volumes}")
    print(f"pitches:{pitches}")
    
    # Initialize list for steps
    steps_list = []
    for i in range(1, len(samples) + 1):
       # Collecting each sample's steps.
        steps = request.form.getlist(f'steps[{i}][]')
        steps_str = ','.join(steps) # Joining step values with commas
        steps_list.append(steps_str)


    with open('pattern.csv', 'w', newline='') as csvfile:
        # BPM at the top
        csvfile.write(f"{bpm}\n")
        # Iterate through and construct each row
        for sample, volume, pitch, steps_str in zip(samples, volumes, pitches, steps_list):
            row = f"{sample},{volume},{pitch},{steps_str}\n"
            csvfile.write(row)
 
    audio_file = 'output.wav'
    output_path = os.path.join('static', audio_file)
    construct_audio('pattern.csv', output_path)
    return jsonify({'audio_path': url_for('static', filename=audio_file)})

if __name__ == "__main__":
    app.run(debug=False)
