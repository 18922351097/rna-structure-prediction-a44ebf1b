import os
from flask import Flask, render_template, request, jsonify
from RNA import fold, PS_rna_plot
import base64
import tempfile
import RNA

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
        (ss, mfe) = fold(sequence)
        print(f"Predicted structure: {ss}")
        print(f"Minimum free energy: {mfe}")
        
        # Generate 2D plot
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
            PS_rna_plot(sequence, ss, tmp.name)
            with open(tmp.name, 'rb') as f:
                svg_data = f.read()
        os.unlink(tmp.name)
        
        svg_base64 = base64.b64encode(svg_data).decode('utf-8')
        
        response_data = {
            'sequence': sequence,
            'structure': ss,
            'mfe': mfe,
            'svg': svg_base64
        }
        print("Sending response:", response_data)
        return jsonify(response_data)
    except Exception as e:
        print(f"Error in predict route: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
