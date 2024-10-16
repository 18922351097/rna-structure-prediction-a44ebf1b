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
            if (data && data.sequence && data.structure && data.mfe && data.plot && data.graph_data) {
                loading.style.display = 'none';

                document.getElementById('result-sequence').textContent = data.sequence;
                document.getElementById('result-structure').textContent = data.structure;
                document.getElementById('result-mfe').textContent = data.mfe;

                // Display RNA plot
                displayRNAPlot(data.plot);

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

function displayRNAPlot(imgData) {
    const structureViz = document.getElementById('structure-viz');
    structureViz.innerHTML = `<img src="data:image/png;base64,${imgData}" alt="RNA Structure Visualization">`;
}

function createForceGraph(graphData) {
    const width = 400;
    const height = 300;

    d3.select("#force-graph").selectAll("*").remove();

    const svg = d3.select("#force-graph")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    const simulation = d3.forceSimulation(graphData.nodes)
        .force("link", d3.forceLink(graphData.links).id(d => d.id))
        .force("charge", d3.forceManyBody().strength(-100))
        .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g")
        .selectAll("line")
        .data(graphData.links)
        .enter().append("line")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .attr("stroke-width", 2);

    const node = svg.append("g")
        .selectAll("circle")
        .data(graphData.nodes)
        .enter().append("circle")
        .attr("r", d => getNodeRadius(d))
        .attr("fill", d => getNodeColor(d));

    node.append("title")
        .text(d => `${d.id} (${d.type}, length: ${d.length})`);

    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
    });

    // Add legend
    const legend = svg.append("g")
        .attr("class", "legend")
        .attr("transform", "translate(10, 10)");

    const legendData = [
        {type: "stem", color: "#1f77b4"},
        {type: "hairpin", color: "#2ca02c"},
        {type: "interior_loop", color: "#d62728"},
        {type: "multiloop", color: "#9467bd"},
        {type: "fiveprime", color: "#8c564b"},
        {type: "threeprime", color: "#e377c2"}
    ];

    legend.selectAll("rect")
        .data(legendData)
        .enter()
        .append("rect")
        .attr("x", 0)
        .attr("y", (d, i) => i * 20)
        .attr("width", 10)
        .attr("height", 10)
        .attr("fill", d => d.color);

    legend.selectAll("text")
        .data(legendData)
        .enter()
        .append("text")
        .attr("x", 15)
        .attr("y", (d, i) => i * 20 + 9)
        .text(d => d.type)
        .attr("font-size", "10px")
        .attr("fill", "white");
}

function getNodeRadius(node) {
    const baseRadius = 5;
    return baseRadius + node.length / 2;
}

function getNodeColor(node) {
    switch (node.type) {
        case "stem": return "#1f77b4";
        case "hairpin": return "#2ca02c";
        case "interior_loop": return "#d62728";
        case "multiloop": return "#9467bd";
        case "fiveprime": return "#8c564b";
        case "threeprime": return "#e377c2";
        default: return "#7f7f7f";
    }
}
