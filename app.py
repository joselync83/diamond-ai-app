from flask import Flask, render_template, request
from transformers import pipeline
import openai
import os

# Inicializar la app
app = Flask(__name__)

# Configurar API key de OpenAI desde variable de entorno
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Cargar modelos de traducción
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

    # Obtener el traductor correcto
    translator = translator_models.get((source_lang, target_lang))
    if not translator:
        return "Idioma no soportado", 400

    # Mejorar texto
    improved_text = refine_text_with_openai(text, source_lang)

    # Traducir texto mejorado
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
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"Eres un editor profesional que mejora textos en {lang}."},
            {"role": "user", "content": f"Mejora este texto en {lang}:\n\n{text}"}
        ],
        max_tokens=500
    )
    return response.choices[0].message['content'].strip()

# Este bloque es requerido para Cloud Run / Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))  # Usa 8080 por defecto
    app.run(host='0.0.0.0', port=port)
