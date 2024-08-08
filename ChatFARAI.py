//dilarang copy paste ! 
//dibuat oleh Farrel

from flask import Flask, request, jsonify, render_template_string
import requests
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})  # Menggunakan cache sederhana

@cache.memoize(timeout=60)
def get_openai_response(text):
    if text.lower().startswith("buatkan gambar"):
        prompt = text[len("buatkan gambar"):].strip()
        image_request_url = f"https://itzpire.com/ai/emi?prompt={prompt}"
        try:
            response = requests.get(image_request_url)
            response.raise_for_status()
            data = response.json()
            image_url = data.get("result")
            print(f"Generated image URL: {image_url}")  # Debug: Tampilkan URL gambar yang dihasilkan
            return {"image_url": image_url}
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")  # Debug: Tampilkan kesalahan
            return {"result": "ChatFARAI: Terjadi kesalahan dalam menghasilkan gambar."}
    else:
        url = "https://widipe.com/openai"
        params = {"text": text}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            result = data.get("result", "Terjadi kesalahan.")
            return {"result": f"ChatFARAI: {result}"}
        except requests.exceptions.RequestException as e:
            return {"result": "ChatFARAI: Terjadi kesalahan."}

@app.route('/api/get-response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_input = data.get('text')
    print(f"Received input: {user_input}")  # Debug: Tampilkan input yang diterima
    result = get_openai_response(user_input)
    print(f"Sending response: {result}")  # Debug: Tampilkan hasil respons
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
