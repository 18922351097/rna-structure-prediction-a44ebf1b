# RNA Secondary Structure Prediction and Visualization

This project is a web application that predicts and visualizes RNA secondary structures using Flask, ViennaRNA, and D3.js. It provides a user-friendly interface for inputting RNA sequences and displays the predicted structure along with additional information.

## Features

- RNA secondary structure prediction using ViennaRNA
- Visualization of RNA structure using D3.js
- Minimum free energy calculation
- Force-directed graph representation of RNA structure
- Responsive web interface

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/rna-structure-prediction.git
   cd rna-structure-prediction
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Flask application:
   ```
   python main.py
   ```

2. Open a web browser and navigate to `http://localhost:5000`

3. Enter an RNA sequence in the input field and click "Predict Structure"

4. View the predicted structure, minimum free energy, and force-directed graph

## Dependencies

- Flask
- ViennaRNA
- Matplotlib
- forgi
- D3.js

## API Endpoints

- `/`: Home page
- `/predict` (POST): Accepts RNA sequence and returns prediction results

## Contributors

- [Your Name]

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
