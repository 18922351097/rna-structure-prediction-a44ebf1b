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
            if (!data.sequence || !data.structure || !data.mfe || !data.svg) {
                throw new Error('Incomplete data received from server');
            }
            loading.style.display = 'none';

            document.getElementById('result-sequence').textContent = data.sequence;
            console.log('Updated sequence:', document.getElementById('result-sequence').textContent);

            document.getElementById('result-structure').textContent = data.structure;
            console.log('Updated structure:', document.getElementById('result-structure').textContent);

            document.getElementById('result-mfe').textContent = data.mfe;
            console.log('Updated MFE:', document.getElementById('result-mfe').textContent);

            // Display the SVG
            const structureViz = document.getElementById('structure-viz');
            structureViz.innerHTML = atob(data.svg);
            console.log('Updated SVG:', structureViz.innerHTML);

            // Make sure the SVG is visible and responsive
            const svg = structureViz.querySelector('svg');
            svg.setAttribute('width', '100%');
            svg.setAttribute('height', 'auto');
            console.log('SVG attributes set');

            // Show results
            results.style.display = 'block';
            console.log('Results display set to block');
        })
        .catch(error => {
            console.error('Error:', error);
            loading.style.display = 'none';
            errorMessage.textContent = `An error occurred: ${error.message}. Please try again.`;
            errorMessage.style.display = 'block';
        });
    });
});
