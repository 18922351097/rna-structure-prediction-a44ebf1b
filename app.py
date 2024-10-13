import os
from flask import Flask, render_template, request, jsonify
import RNA
import base64
import tempfile
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
        
        # Create forgi graph
        bg = fgb.BulgeGraph.from_dotbracket(ss)
        graph_data = {
            'nodes': [{'id': elem.define, 'type': elem.nt_type} for elem in bg.defines.values()],
            'links': [{'source': e1, 'target': e2} for e1, e2 in bg.edges()]
        }

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
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
