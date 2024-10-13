document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('rna-form');
    const results = document.getElementById('results');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);

        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('result-sequence').textContent = data.sequence;
            document.getElementById('result-structure').textContent = data.structure;
            document.getElementById('result-mfe').textContent = data.mfe;

            // Display the SVG
            const structureViz = document.getElementById('structure-viz');
            structureViz.innerHTML = atob(data.svg);

            // Make sure the SVG is visible and responsive
            const svg = structureViz.querySelector('svg');
            svg.setAttribute('width', '100%');
            svg.setAttribute('height', 'auto');

            // Show results
            results.style.display = 'block';
        })
        .catch(error => console.error('Error:', error));
    });
});
