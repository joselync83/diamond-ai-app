from flask import Flask, render_template, request
from transformers import pipeline
from openai import OpenAI

# Configurar cliente OpenAI
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# Crear los pipelines de traducción
translator_en_to_es = pipeline("translation", model="Helsinki-NLP/opus-mt-en-es")
translator_es_to_en = pipeline("translation", model="Helsinki-NLP/opus-mt-es-en")
translator_en_to_fr = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr")
translator_fr_to_en = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")
translator_es_to_fr = pipeline("translation", model="Helsinki-NLP/opus-mt-es-fr")
translator_fr_to_es = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-es")

@app.route('/')
def index():
    return render_template('index.html', source_lang='en', target_lang='es', translated_text=None, improved_text=None)

@app.route('/translate', methods=['POST'])
def translate():
    text = request.form['text']
    source_lang = request.form['source_lang']
    target_lang = request.form['target_lang']

    # Selección del traductor
    if source_lang == 'en' and target_lang == 'es':
        translator = translator_en_to_es
    elif source_lang == 'es' and target_lang == 'en':
        translator = translator_es_to_en
    elif source_lang == 'en' and target_lang == 'fr':
        translator = translator_en_to_fr
    elif source_lang == 'fr' and target_lang == 'en':
        translator = translator_fr_to_en
    elif source_lang == 'es' and target_lang == 'fr':
        translator = translator_es_to_fr
    elif source_lang == 'fr' and target_lang == 'es':
        translator = translator_fr_to_es
    else:
        return "Idioma no soportado", 400

    # Primero mejorar el texto original
    improved_text = refine_text_with_openai(text, source_lang)

    # Luego traducir el texto mejorado
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
            {"role": "user", "content": f"Mejora este texto en {lang}:\\n\\n{text}"}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

if __name__ == '__main__':
    app.run(debug=True)
