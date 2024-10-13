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
            if (data && data.sequence && data.structure && data.mfe && data.graph_data) {
                loading.style.display = 'none';

                document.getElementById('result-sequence').textContent = data.sequence;
                document.getElementById('result-structure').textContent = data.structure;
                document.getElementById('result-mfe').textContent = data.mfe;

                // Create force-directed graph
                createForceGraph(data.graph_data);

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

function createForceGraph(data) {
    const width = 600;
    const height = 400;
    
    const svg = d3.select('#structure-viz').html('').append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.links).id(d => d.id))
        .force('charge', d3.forceManyBody())
        .force('center', d3.forceCenter(width / 2, height / 2));
    
    const link = svg.append('g')
        .selectAll('line')
        .data(data.links)
        .enter().append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6);
    
    const node = svg.append('g')
        .selectAll('circle')
        .data(data.nodes)
        .enter().append('circle')
        .attr('r', 5)
        .attr('fill', d => d.type === 's' ? '#ff0000' : '#00ff00');
    
    node.append('title')
        .text(d => d.id);
    
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
    });
}
