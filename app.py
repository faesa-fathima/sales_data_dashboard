from flask import Flask, render_template, request, send_file
import pandas as pd
import os
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORT_FOLDER'] = 'static/reports'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(app.config['REPORT_FOLDER']):
    os.makedirs(app.config['REPORT_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            df = pd.read_csv(filepath, parse_dates=['Date'])
            df['Month'] = df['Date'].dt.to_period('M')
            monthly_sales = df.groupby('Month')['Sales'].sum()
            plt.figure()
            monthly_sales.plot(kind='bar', title='Monthly Sales')
            chart_path = os.path.join(app.config['REPORT_FOLDER'], 'monthly_sales.png')
            plt.tight_layout()
            plt.savefig(chart_path)
            return render_template('dashboard.html', image_file=chart_path, tables=[df.head().to_html(classes='data')], titles=df.columns.values)
    return render_template('index.html')

@app.route('/download_report')
def download_report():
    report_path = os.path.join(app.config['REPORT_FOLDER'], 'monthly_sales.png')
    return send_file(report_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)