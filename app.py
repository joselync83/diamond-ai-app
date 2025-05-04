from flask import Flask, render_template, request
from transformers import pipeline
from openai import OpenAI
import os

# Inicializar la app
app = Flask(__name__)

# Configurar cliente OpenAI (usa variable de entorno en producción)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Cargar los modelos una sola vez (memoria eficiente)
translator_models = {
    ("en", "es"): pipeline("translation", model="Helsinki-NLP/opus-mt-en-es"),
    ("es", "en"): pipeline("translation", model="Helsinki-NLP/opus-mt-es-en"),
    ("en", "fr"): pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr"),
    ("fr", "en"): pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en"),
    ("es", "fr"): pipeline("translation", model="Helsinki-NLP/opus-mt-es-fr"),
    ("fr", "es"): pipeline("translation", model="Helsinki-NLP/opus-mt-fr-es"),
}

@app.route('/')
def index():
    return render_template('index.html', source_lang='en', target_lang='es', translated_text=None, improved_text=None)

@app.route('/translate', methods=['POST'])
def translate():
    text = request.form['text']
    source_lang = request.form['source_lang']
    target_lang = request.form['target_lang']

    # Verificar si el par de idiomas es válido
    translator = translator_models.get((source_lang, target_lang))
    if not translator:
        return "Idioma no soportado", 400

    # Paso 1: Mejorar texto con OpenAI
    improved_text = refine_text_with_openai(text, source_lang)

    # Paso 2: Traducir texto mejorado
    result = translator(improved_text)
    translated_text = result[0]['translation_text']

    return render_template(
        'index.html',
        translated_text=translated_text,
        improved_text=improved_text,
        source_lang=source_lang,
        target_lang=target_lang
    )

def refine_text_with_openai(text, lang):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Eres un editor profesional que mejora textos en {lang}."},
            {"role": "user", "content": f"Mejora este texto en {lang}:\n\n{text}"}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

# Puerto compatible con Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
