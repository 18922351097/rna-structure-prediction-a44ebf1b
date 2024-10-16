import os
import logging
from flask import Flask, render_template, request, jsonify
import RNA
import base64
import io
import matplotlib.pyplot as plt
import forgi
import forgi.graph.bulge_graph as fgb
import forgi.visual.mplotlib as fvm
import traceback

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

logging.debug("Starting application...")
logging.debug("ViennaRNA version: %s", RNA.__version__)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"

@app.route('/')
def index():
    logging.debug("Rendering index page")
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        logging.debug('Received POST request to /predict')
        sequence = request.form['sequence']
        logging.debug(f"Received sequence: {sequence}")
        
        if not sequence:
            raise ValueError("Empty sequence received")
        
        # Predict secondary structure
        (ss, mfe) = RNA.fold(sequence)
        logging.debug(f"Predicted structure: {ss}")
        logging.debug(f"Minimum free energy: {mfe}")
        
        # Generate graph data
        bg = fgb.BulgeGraph.from_dotbracket(ss, seq=sequence)
        graph_data = generate_graph_data(bg)
        
        # Generate plot
        plt.figure(figsize=(10, 10))
        plot_rna_structure(bg, sequence)
        
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
        logging.debug("Sending response: %s", response_data)
        return jsonify(response_data)
    except Exception as e:
        logging.error(f"Error in predict route: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

def generate_graph_data(bg):
    nodes = []
    links = []
    try:
        for e in bg.defines:
            element_type = bg.get_element_type(e)  # Changed from get_node_type to get_element_type
            define = bg.defines[e]
            node = {'id': e, 'type': element_type, 'length': len(define)}
            if element_type == 'stem':
                node['length'] = len(define) // 2
            nodes.append(node)
        
        for e1, e2 in bg.edges():
            links.append({'source': e1, 'target': e2})
        
        logging.debug("Generated graph data: %s", {'nodes': nodes, 'links': links})
    except Exception as e:
        logging.error(f"Error in generate_graph_data: {str(e)}")
        logging.error(traceback.format_exc())
    
    return {'nodes': nodes, 'links': links}

def plot_rna_structure(bg, sequence):
    if len(sequence) <= 500:
        fvm.plot_rna(bg, text_kwargs={"fontweight":"bold"})
    else:
        fvm.plot_rna(bg, text_kwargs={"fontweight":"bold"}, show_letters=False)
    plt.axis('off')

if __name__ == '__main__':
    try:
        logging.info("Starting Flask application...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logging.error(f"Error starting Flask application: {str(e)}")
        logging.error(traceback.format_exc())
