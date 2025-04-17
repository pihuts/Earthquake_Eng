```markdown
# Structural Portal Frame Analysis

A Python-based project for analyzing structural portal frame behavior using numerical methods, scientific libraries, and custom-built modules to compute and visualize forces on columns and beams in multi-story, multi-bay configurations.

## Features
- **Coordinate Generation:** Creates 2D grid of nodes with automatic NaN placement where needed
- **Node Labeling:** Automatically generates alphanumeric labels for nodes using a dictionary system
- **Structured Arrays:** Captures shear, moment, and axial forces in structured NumPy arrays
- **Mathematical Documentation:** Stores step-by-step calculations in LaTeX format
- **HTML Visualization:** Generates HTML files with MathJax for rendering complex equations
- **Automated Screenshot Capture:** Uses Selenium to capture screenshots of generated HTML equations
- **Data Chunking:** Implements efficient handling of large datasets by chunking data into manageable sizes
- **Graphical Plots:** Renders moment, shear, and axial-force diagrams in 2D context

## Requirements
This project requires Python 3.7+ and the following libraries (specific versions listed):

- numpy==2.2.4
- pandas==2.2.3
- matplotlib==3.10.1
- scikit-learn==1.6.1
- scipy==1.15.2
- selenium (for HTML screenshots)
- chromedriver.exe (for Selenium WebDriver functionality)

Additional dependencies are listed in `requirements.txt`.

## Installation
1. Clone or download this repository
2. Install dependencies using pip:
   ```
   pip install -r requirements.txt
   ```
3. Place `chromedriver.exe` in your PATH or in the project's working directory

## Usage
1. **Configure Portal Frame Data**
   Edit the arrays in `UTILITIES_APPROX.py` such as `ForceList`, `BuildingHeightList`, `BuildingSpanList`, and `NanList` to match your building configuration.

2. **Run Main Scripts**
   ```
   python PORTAL_APPROX.py
   ```

3. **Output Files**
   - CSV files containing moment, shear, and axial forces data
   - HTML files in the `Beam` folder showing LaTeX equations and calculations
   - Screenshot images in the `Solutions` folder (or custom named folder)
   - Structured array outputs with force distributions

## Project Structure
- `PORTAL_APPROX.py`: Main script orchestrating the force generation process
- `UTILITIES_APPROX.py`: Contains utility functions for:
  - Coordinate generation and node labeling
  - LaTeX data generation and HTML rendering
  - Folder creation and file management
  - Array manipulation and data chunking
  - Selenium screenshot functionality
- `PLOTTER_APPROX.py`: Optional plotting module for visualizing results

## Key Functions
- `Create3DArray`: Generates nodal coordinate system and alphanumeric labels
- `AppendStructuredArray`: Handles structured data arrays for forces
- `add_latex_data`: Stores calculation steps with descriptions
- `selenium_screenshot`: Creates visual documentation by capturing HTML outputs
- `html_makerl`: Generates HTML tables with LaTeX content using MathJax

## Troubleshooting
- **Selenium Issues**: Ensure chromedriver.exe version matches your Chrome browser
- **HTML Rendering**: Check MathJax CDN connectivity if equations don't render
- **Data Processing**: Verify coordinate systems match between NanList and NodesArrays

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss proposed modifications.

## License
No explicit license specified. Please contact the repository owner for usage permissions.
```