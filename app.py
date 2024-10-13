import os
from flask import Flask, render_template, request, jsonify
from RNA import fold, PS_rna_plot
import base64
import tempfile

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    sequence = request.form['sequence']
    
    # Predict secondary structure
    (ss, mfe) = fold(sequence)
    
    # Generate 2D plot
    with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
        PS_rna_plot(sequence, ss, tmp.name)
        with open(tmp.name, 'rb') as f:
            svg_data = f.read()
    os.unlink(tmp.name)
    
    svg_base64 = base64.b64encode(svg_data).decode('utf-8')
    
    return jsonify({
        'sequence': sequence,
        'structure': ss,
        'mfe': mfe,
        'svg': svg_base64
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
