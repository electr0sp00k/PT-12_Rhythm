from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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

    return 'CSV updated'

if __name__ == "__main__":
    app.run(debug=True)
