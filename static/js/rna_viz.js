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
    console.log('Creating force graph with data:', data);
    const width = 600;
    const height = 400;
    
    const svg = d3.select('#structure-viz').html('').append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-200))
        .force('center', d3.forceCenter(width / 2, height / 2));
    
    const link = svg.append('g')
        .selectAll('line')
        .data(data.links)
        .enter().append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', 2);
    
    const node = svg.append('g')
        .selectAll('circle')
        .data(data.nodes)
        .enter().append('circle')
        .attr('r', 10)
        .attr('fill', d => d.type === 'stem' ? '#ff0000' : '#00ff00')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    const label = svg.append('g')
        .selectAll('text')
        .data(data.nodes)
        .enter().append('text')
        .text(d => d.id)
        .attr('font-size', '12px')
        .attr('dx', 12)
        .attr('dy', 4);
    
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });
    
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}
