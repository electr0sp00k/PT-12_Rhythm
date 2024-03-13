document.addEventListener('DOMContentLoaded', function() {
    // AJAX form submission
    const form = document.getElementById('sequence');
    form.onsubmit = function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        fetch('/update_csv', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            let audioPlayer = document.querySelector('audio');
            // If no audioplayer loaded, load one
            if (!audioPlayer) {
                audioPlayer = document.createElement('audio');
                audioPlayer.controls = true;
                document.body.appendChild(audioPlayer);
            }
            // Time Stamp to cachebash
            const timestamp = new Date().getTime();
            // Serve the newly baked audio loop
            audioPlayer.innerHTML = `<source src="${data.audio_path}?${timestamp}" type="audio/wav">Audio playback not supported in your browser.`;
            audioPlayer.load();
        })
        .catch(error => console.error('Error:', error));
    };
    const addSampleButton = document.getElementById('add-sample-btn');
    if (addSampleButton) {
        addSampleButton.addEventListener('click', addSample);
    }
});

function addSample() {
    const samplesDiv = document.getElementById('samples');

    const sampleDiv = document.createElement('div');
    sampleDiv.className = 'sample';

    // sample selector
    const sampleSelect = document.createElement('select');
    sampleSelect.name = 'samples[]';

    // Fetch sample list from flask
    fetch('/list_samples')
        .then(response => response.json())
        .then(files => {
            files.forEach(file => {
                const option = document.createElement('option');
                option.value = file;
                option.textContent = file;
                sampleSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching sample files:', error));
    sampleDiv.appendChild(sampleSelect);

    // Volume input
    const volumeInput = createInput('volume', 'Volume: % of original');
    sampleDiv.appendChild(volumeInput);

    // Pitch input
    const pitchInput = createInput('pitch', 'Pitch: +/- Semitones');
    sampleDiv.appendChild(pitchInput);

    // Steps container
    const stepsDiv = document.createElement('div');
    stepsDiv.className = 'steps-container';
    sampleDiv.appendChild(stepsDiv);

    const sampleIndex = samplesDiv.children.length;
    // Add step button
    const addStepBtn = createButton('+ Step', () => addStep(stepsDiv, sampleIndex));
    sampleDiv.appendChild(addStepBtn);

    // Remove step button
    const removeStepBtn = createButton('- Step', () => removeStep(stepsDiv));
    sampleDiv.appendChild(removeStepBtn);

    // Remove sample button
    const removeSampleBtn = createButton('Remove Sample', () => samplesDiv.removeChild(sampleDiv));
    sampleDiv.appendChild(removeSampleBtn);

    samplesDiv.appendChild(sampleDiv);
}

function addStep(parentDiv, sampleIndex) {
    const stepIndex = parentDiv.querySelectorAll('.step-button').length;
    const stepButton = document.createElement('div');
    stepButton.className = 'step-button';
    stepButton.textContent = stepIndex + 1;

    // Hidden input for step state
    const stepInput = document.createElement('input');
    stepInput.type = 'hidden';
    stepInput.name = `steps[${sampleIndex}][]`;
    stepInput.value = '0';

    // Toggle between on and off
    stepButton.onclick = () => {
        stepButton.classList.toggle('active');
        stepInput.value = stepButton.classList.contains('active') ? '1' : '0';
    };

    parentDiv.appendChild(stepButton);
    parentDiv.appendChild(stepInput);
}


function createInput(name, placeholder) {
    const input = document.createElement('input');
    input.type = 'number';
    input.name = `${name}[]`;
    input.placeholder = placeholder;
    return input;
}

function createButton(text, onClick) {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = text;
    button.onclick = onClick;
    return button;
}

function removeStep(stepsContainer) {

    // Get all step elements
    const stepButtons = stepsContainer.querySelectorAll('.step-button');
    const stepInputs = stepsContainer.querySelectorAll('input[type="hidden"]');

    // Check if there are any step buttons to remove
    if (stepButtons.length > 0) {
        // Remove the last step button
        const lastStepButton = stepButtons[stepButtons.length - 1];
        lastStepButton.parentNode.removeChild(lastStepButton);
    }

    // Check if there are any hidden inputs to remove
    if (stepInputs.length > 0) {
        // Remove the last hidden input
        const lastStepInput = stepInputs[stepInputs.length - 1];
        lastStepInput.parentNode.removeChild(lastStepInput);
    }
}
