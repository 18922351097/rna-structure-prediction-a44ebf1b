import os
from flask import Flask, render_template, request, jsonify
import RNA
import base64
import io
import matplotlib.pyplot as plt
import forgi.graph.bulge_graph as fgb
import forgi.visual.mplotlib as fvm
import traceback

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
        bg = fgb.BulgeGraph.from_dotbracket(ss, seq=sequence)
        graph_data = generate_graph_data(bg)
        
        # Generate plot
        plt.figure(figsize=(10, 10))
        plot_rna_structure(bg)
        
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
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

def generate_graph_data(bg):
    nodes = []
    links = []
    try:
        for e in bg.defines:
            element_type = bg.element_type(e)
            define = bg.defines[e]
            node = {'id': e, 'type': element_type, 'length': len(define)}
            if element_type == 'stem':
                node['length'] = len(define) // 2
            nodes.append(node)
        
        for e1, e2 in bg.edges():
            links.append({'source': e1, 'target': e2})
        
        print("Generated graph data:", {'nodes': nodes, 'links': links})
    except Exception as e:
        print(f"Error in generate_graph_data: {str(e)}")
        print(traceback.format_exc())
    
    return {'nodes': nodes, 'links': links}

def plot_rna_structure(bg):
    fvm.plot_rna(bg, text_kwargs={"fontweight":"bold"})
    plt.axis('off')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
