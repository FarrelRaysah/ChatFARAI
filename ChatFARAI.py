from flask import Flask, request, jsonify, render_template_string
import requests
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})  # Menggunakan cache sederhana

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Application</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .chat-container {
            width: 400px;
            max-width: 100%;
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            height: 500px;
            overflow: hidden;
        }
        .header {
            background-color: #007bff;
            color: #fff;
            padding: 10px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            border-bottom: 1px solid #ddd;
        }
        .chat-box {
            flex: 1;
            padding: 10px;
            overflow-y: auto;
            border-bottom: 1px solid #ddd;
        }
        .message {
            display: flex;
            margin-bottom: 10px;
            align-items: flex-start;
        }
        .message.user {
            justify-content: flex-end;
        }
        .message.user .text {
            background-color: #007bff;
            color: #fff;
            border-radius: 15px;
            padding: 10px 15px;
            max-width: 70%;
            word-break: break-word;
            text-align: right;
        }
        .message.bot .text {
            background-color: #e9ecef;
            color: #000;
            border-radius: 15px;
            padding: 10px 15px;
            max-width: 70%;
            word-break: break-word;
        }
        .message.bot .image {
            max-width: 70%;
            border-radius: 10px;
            overflow: hidden;
        }
        .input-container {
            display: flex;
            padding: 10px;
            border-top: 1px solid #ddd;
            background-color: #fff;
        }
        input[type="text"] {
            flex: 1;
            border: none;
            border-radius: 20px;
            padding: 10px 15px;
            font-size: 16px;
            margin-right: 10px;
            box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
        }
        button {
            border: none;
            background-color: #007bff;
            color: #fff;
            border-radius: 20px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">ChatFARAI by Farrel</div>
        <div class="chat-box" id="chat-box"></div>
        <div class="input-container">
            <input type="text" id="user-input" placeholder="Type your message..." />
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>
    <script>
        async function sendMessage() {
            const inputField = document.getElementById('user-input');
            const chatBox = document.getElementById('chat-box');
            const userMessage = inputField.value;
            chatBox.innerHTML += `<div class="message user"><div class="text">${userMessage}</div></div>`;
            inputField.value = '';

            try {
                const response = await fetch('/api/get-response', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ text: userMessage })
                });

                const result = await response.json();

                if (result.image_url) {
                    const imageUrl = result.image_url;
                    chatBox.innerHTML += `<div class="message bot"><img class="image" src="${imageUrl}" alt="Generated Image" onerror="this.onerror=null;this.src='/static/error.png';" /></div>`;
                } else if (result.result) {
                    chatBox.innerHTML += `<div class="message bot"><div class="text">${result.result}</div></div>`;
                } else {
                    chatBox.innerHTML += `<div class="message bot"><div class="text">No 'result' field found in API result.</div></div>`;
                }
            } catch (error) {
                chatBox.innerHTML += `<div class="message bot"><div class="text">Error: ${error.message}</div></div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
'''

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

@app.route('/')
def index():
    print("Rendering index page")  # Debug: Tampilkan pesan saat halaman utama dirender
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)