document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('rna-form');
    const results = document.getElementById('results');
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');

    console.log('DOM content loaded, form and results elements:', form, results);

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log('Form submitted');
        const formData = new FormData(form);
        console.log('Form data:', Object.fromEntries(formData));

        loading.style.display = 'block';
        errorMessage.style.display = 'none';
        results.style.display = 'none';

        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log('Response received:', response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Data received:', data);
            if (data && data.sequence && data.structure && data.mfe && data.plot) {
                loading.style.display = 'none';

                document.getElementById('result-sequence').textContent = data.sequence;
                document.getElementById('result-structure').textContent = data.structure;
                document.getElementById('result-mfe').textContent = data.mfe;

                // Display RNA plot
                displayRNAPlot(data.plot);

                // Show results
                results.style.display = 'block';
                console.log('Results display set to block');
            } else {
                console.error('Incomplete data received:', data);
                errorMessage.textContent = 'Incomplete data received from server. Please try again.';
                errorMessage.style.display = 'block';
                loading.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loading.style.display = 'none';
            errorMessage.textContent = `An error occurred: ${error.message}. Please try again.`;
            errorMessage.style.display = 'block';
        });
    });
});

function displayRNAPlot(imgData) {
    const structureViz = document.getElementById('structure-viz');
    structureViz.innerHTML = `<img src="data:image/png;base64,${imgData}" alt="RNA Structure Visualization">`;
}
