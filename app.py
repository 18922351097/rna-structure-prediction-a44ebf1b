import os
from flask import Flask, render_template, request, jsonify
import RNA
import base64
import io
import matplotlib.pyplot as plt
import networkx as nx

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
        
        # Generate graph data
        graph_data = generate_graph_data(ss)
        
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

def generate_graph_data(structure):
    G = nx.Graph()
    stack = []
    for i, char in enumerate(structure):
        if char == '(':
            stack.append(i)
        elif char == ')':
            if stack:
                start = stack.pop()
                G.add_edge(start, i)
    
    pos = nx.spring_layout(G)
    nodes = [{'id': str(n), 'x': pos[n][0], 'y': pos[n][1]} for n in G.nodes()]
    links = [{'source': str(u), 'target': str(v)} for u, v in G.edges()]
    
    return {'nodes': nodes, 'links': links}

def plot_rna_structure(sequence, structure):
    plt.text(0.5, 0.5, structure, ha='center', va='center', fontsize=20)
    plt.text(0.5, 0.4, sequence, ha='center', va='center', fontsize=16)
    plt.axis('off')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
