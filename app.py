import os
from flask import Flask, render_template, request, jsonify
import RNA
import base64
import io
import matplotlib.pyplot as plt
import networkx as nx
import forgi.graph.bulge_graph as fgb

print("ViennaRNA version:", RNA.__version__)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        print("Received POST request to /predict")
        sequence = request.form['sequence']
        print(f"Received sequence: {sequence}")
        
        if not sequence:
            raise ValueError("Empty sequence received")
        
        # Predict secondary structure
        (ss, mfe) = RNA.fold(sequence)
        print(f"Predicted structure: {ss}")
        print(f"Minimum free energy: {mfe}")
        
        # Generate graph data using forgi
        bg = fgb.BulgeGraph.from_dotbracket(ss)
        graph_data = generate_graph_data(bg)
        
        # Generate plot
        plt.figure(figsize=(10, 10))
        plot_rna_structure(sequence, ss)
        
        # Save plot to a BytesIO object
        img_io = io.BytesIO()
        plt.savefig(img_io, format='png')
        img_io.seek(0)
        img_data = base64.b64encode(img_io.getvalue()).decode()
        
        plt.close()  # Close the plot to free up memory
        
        response_data = {
            'sequence': sequence,
            'structure': ss,
            'mfe': mfe,
            'plot': img_data,
            'graph_data': graph_data
        }
        print("Sending response:", response_data)
        return jsonify(response_data)
    except Exception as e:
        print(f"Error in predict route: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_graph_data(bg):
    nodes = []
    links = []
    for e, define in bg.defines.items():
        if e.startswith('s'):
            nodes.append({'id': e, 'type': 'stem', 'length': len(define) // 2})
        elif e.startswith('h'):
            nodes.append({'id': e, 'type': 'hairpin', 'length': len(define)})
        elif e.startswith('i'):
            nodes.append({'id': e, 'type': 'interior_loop', 'length': len(define)})
        elif e.startswith('m'):
            nodes.append({'id': e, 'type': 'multiloop', 'length': len(define)})
        elif e.startswith('f'):
            nodes.append({'id': e, 'type': 'fiveprime', 'length': len(define)})
        elif e.startswith('t'):
            nodes.append({'id': e, 'type': 'threeprime', 'length': len(define)})
    
    for e1, e2 in bg.edges:  # Changed from bg.edges() to bg.edges
        links.append({'source': e1, 'target': e2})
    
    return {'nodes': nodes, 'links': links}

def plot_rna_structure(sequence, structure):
    plt.text(0.5, 0.5, structure, ha='center', va='center', fontsize=20)
    plt.text(0.5, 0.4, sequence, ha='center', va='center', fontsize=16)
    plt.axis('off')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
