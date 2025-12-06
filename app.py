import os
import pickle
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import numpy as np

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'change-me-for-production')

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'model.pkl')
PREPROCESSOR_PATH = os.path.join(os.path.dirname(__file__), 'models', 'preprocessor.pkl')
LABEL_ENCODER_PATH = os.path.join(os.path.dirname(__file__), 'models', 'label_encoder.pkl')

def try_load(path):
    """Try to load an artifact using joblib (preferred) then pickle as fallback.

    This handles artifacts saved with joblib.dump (possibly compressed) and
    with pickle.dump. Returns the loaded object or None if not found/cannot load.
    """
    if not os.path.exists(path):
        return None
    # Try joblib first (handles compressed/joblib format)
    try:
        import joblib
        return joblib.load(path)
    except Exception:
        pass
    # Fallback to pickle
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return None

model = try_load(MODEL_PATH)
preprocessor = try_load(PREPROCESSOR_PATH)
label_encoder = try_load(LABEL_ENCODER_PATH)

DEFAULT_LABELS = {0: 'Dropout', 1: 'Enrolled', 2: 'Graduate'}

FEATURES = [
    'Marital Status',
    'Application mode',
    'Application order',
    'Course',
    'Daytime/evening attendance',
    'Previous qualification',
    'Previous qualification (grade)',
    'Nacionality',
    "Mother's qualification",
    "Father's qualification",
    "Mother's occupation",
    "Father's occupation",
    'Admission grade',
    'Displaced',
    'Educational special needs',
    'Debtor',
    'Tuition fees up to date',
    'Gender',
    'Scholarship holder',
    'Age at enrollment',
    'International',
    'Curricular units 1st sem (credited)',
    'Curricular units 1st sem (enrolled)',
    'Curricular units 1st sem (evaluations)',
    'Curricular units 1st sem (approved)',
    'Curricular units 1st sem (grade)',
    'Curricular units 1st sem (without evaluations)',
    'Curricular units 2nd sem (credited)',
    'Curricular units 2nd sem (enrolled)',
    'Curricular units 2nd sem (evaluations)',
    'Curricular units 2nd sem (approved)',
    'Curricular units 2nd sem (grade)',
    'Curricular units 2nd sem (without evaluations)',
    'Unemployment rate',
    'Inflation rate',
    'GDP'
]

@app.route('/')
def home():
    # choose a hero image from static/img if available
    img_dir = os.path.join(os.path.dirname(__file__), 'static', 'img')
    hero = None
    if os.path.exists(img_dir):
        # prefer notebook_image_6_0.png (large plot) then first file
        preferred = ['notebook_image_6_0.png', 'notebook_image_0_0.png']
        files = [f for f in os.listdir(img_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.webp'))]
        files.sort()
        for p in preferred:
            if p in files:
                hero = p
                break
        if hero is None and len(files) > 0:
            hero = files[0]
    return render_template('home.html', hero_image=hero)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/gallery')
def gallery():
    # List image files from static/img
    img_dir = os.path.join(os.path.dirname(__file__), 'static', 'img')
    files = []
    if os.path.exists(img_dir):
        for f in os.listdir(img_dir):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.webp')):
                files.append(f)
    files.sort()
    return render_template('gallery.html', images=files)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        if not name or not email or not message:
            flash('Mohon isi semua field kontak.', 'danger')
            return redirect(url_for('contact'))
        flash('Pesan terkirim. Terima kasih!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    result = None
    probabilities = None
    if request.method == 'POST':
        data = {}
        errors = []
        for feat in FEATURES:
            val = request.form.get(feat)
            if val is None or val == '':
                errors.append(f'Field "{feat}" wajib diisi.')
            else:
                data[feat] = val

        if errors:
            for e in errors:
                flash(e, 'danger')
            return redirect(url_for('predict'))

        row = []
        for feat in FEATURES:
            raw = data[feat]
            try:
                if raw in ['0', '1'] and feat in ['Tuition fees up to date', 'Scholarship holder']:
                    val = int(raw)
                else:
                    val = float(raw)
            except Exception:
                val = raw
            row.append(val)

        df = pd.DataFrame([row], columns=FEATURES)

        if preprocessor is None or model is None:
            flash('Model atau preprocessor tidak ditemukan. Harap upload `model.pkl` dan `preprocessor.pkl` ke folder /models.', 'danger')
            return redirect(url_for('predict'))

        try:
            X = preprocessor.transform(df)
        except Exception as e:
            flash('Gagal melakukan preprocessing: ' + str(e), 'danger')
            return redirect(url_for('predict'))

        try:
            pred_idx = model.predict(X)
            pred_idx = np.asarray(pred_idx).ravel()
        except Exception as e:
            flash('Gagal melakukan prediksi: ' + str(e), 'danger')
            return redirect(url_for('predict'))

        try:
            if label_encoder is not None:
                labels = label_encoder.inverse_transform(pred_idx)
            else:
                labels = [DEFAULT_LABELS.get(int(i), str(i)) for i in pred_idx]
        except Exception:
            labels = [str(i) for i in pred_idx]

        result = labels[0]

        try:
            if hasattr(model, 'predict_proba'):
                probs = model.predict_proba(X)[0]
                if label_encoder is not None:
                    classes = label_encoder.inverse_transform(np.arange(len(probs)))
                else:
                    classes = [DEFAULT_LABELS.get(i, str(i)) for i in range(len(probs))]
                probabilities = list(zip(classes, [float(p) for p in probs]))
        except Exception:
            probabilities = None

        flash('Prediksi berhasil', 'success')

    return render_template('predict.html', features=FEATURES, result=result, probabilities=probabilities)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
