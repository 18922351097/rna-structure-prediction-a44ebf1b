import os
from flask import Flask, render_template, request, jsonify
import RNA
import base64
import tempfile
import forgi.graph.bulge_graph as fgb
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
        
        # Create forgi graph
        bg = fgb.BulgeGraph.from_dotbracket(ss)
        graph_data = {
            'nodes': [],
            'links': []
        }
        for key, elem in bg.defines.items():
            if isinstance(elem, list):
                graph_data['nodes'].append({'id': key, 'type': 'loop' if key.startswith('h') else 'stem'})
            else:
                print(f"Unexpected element type for key {key}: {type(elem)}")
        
        for e1, e2 in bg.edges():
            graph_data['links'].append({'source': e1, 'target': e2})

        print("Graph data:", graph_data)

        response_data = {
            'sequence': sequence,
            'structure': ss,
            'mfe': mfe,
            'graph_data': graph_data
        }
        print("Sending response:", response_data)
        return jsonify(response_data)
    except Exception as e:
        print(f"Error in predict route: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error args: {e.args}")
        print("Traceback:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
