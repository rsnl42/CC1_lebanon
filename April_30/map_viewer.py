from flask import Flask, render_template, redirect, url_for, send_from_directory
import os

app = Flask(__name__)

MAP_DIR = os.path.join(os.getcwd(), 'April_30') # Absolute path to the April_30 directory
MAP_FILENAMES = {
    '2000': 'PWD_2000_sub_national_100m_map.html',
    '2005': 'PWD_2005_sub_national_100m_map.html',
    '2010': 'PWD_2010_sub_national_100m_map.html',
    '2015': 'PWD_2015_sub_national_100m_map.html',
    '2020': 'PWD_2020_sub_national_100m_map.html',
}
AVAILABLE_YEARS = sorted(MAP_FILENAMES.keys(), reverse=True) # Sort in descending order

@app.route('/')
def index():
    # Redirect to the most recent map by default
    return redirect(url_for('show_map', year=AVAILABLE_YEARS[0]))

@app.route('/map/<year>')
def show_map(year):
    if year not in MAP_FILENAMES:
        return "Map not found for this year.", 404
    
    map_filename = MAP_FILENAMES[year]
    # The map files are in the same directory as this script.
    # We will pass the filename to the template, and the template will load it via iframe
    return render_template('index.html', 
                           selected_year=year, 
                           available_years=AVAILABLE_YEARS,
                           map_filename=map_filename)

@app.route('/maps/<path:filename>')
def serve_map_file(filename):
    # This route will serve the actual HTML map files
    # It ensures that only files from MAP_FILENAMES can be served
    if filename not in MAP_FILENAMES.values():
        return "File not found.", 404
    return send_from_directory(MAP_DIR, filename)

if __name__ == '__main__':
    # For development, run with debug=True
    # In production, use a production-ready WSGI server like Gunicorn or uWSGI
    app.run(debug=True, port=5000)
