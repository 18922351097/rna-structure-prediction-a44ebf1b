import os
from flask import Flask, render_template, request, jsonify
import RNA
import base64
import tempfile
import forgi.graph.bulge_graph as fgb
import traceback
import matplotlib.pyplot as plt
import forgi.visual.mplotlib as fvm
import forgi
import io

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
        bg = fgb.BulgeGraph.from_dotbracket(ss, seq=sequence)
        
        # Generate plot
        plt.figure(figsize=(10, 10))
        fvm.plot_rna(bg, text_kwargs={"fontweight":"black"}, lighten=0.7,
                     backbone_kwargs={"linewidth":3})
        
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
            'plot': img_data
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
