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
            if (data && data.sequence && data.structure && data.mfe && data.svg) {
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
                console.log('SVG content:', structureViz.innerHTML);

                // Make sure the SVG is visible and responsive
                const svg = structureViz.querySelector('svg');
                if (svg) {
                    svg.setAttribute('width', '100%');
                    svg.setAttribute('height', 'auto');
                    console.log('SVG attributes set successfully');
                } else {
                    console.error('SVG element not found in the structure-viz');
                    // If SVG is not found, try to create it manually
                    const parser = new DOMParser();
                    const svgDoc = parser.parseFromString(atob(data.svg), 'image/svg+xml');
                    const svgElement = svgDoc.documentElement;
                    structureViz.appendChild(svgElement);
                    svgElement.setAttribute('width', '100%');
                    svgElement.setAttribute('height', 'auto');
                    console.log('SVG created and appended manually');
                }

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

    // Add SVG download functionality
    const downloadButton = document.getElementById('download-svg');
    downloadButton.addEventListener('click', function() {
        const svgData = new XMLSerializer().serializeToString(document.querySelector('#structure-viz svg'));
        const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
        const svgUrl = URL.createObjectURL(svgBlob);
        const downloadLink = document.createElement('a');
        downloadLink.href = svgUrl;
        downloadLink.download = 'rna_structure.svg';
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
    });
});
