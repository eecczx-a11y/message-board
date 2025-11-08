from flask import Flask, request, jsonify, render_template
import json, os, time, datetime, threading

app = Flask(__name__, template_folder='templates')
DATA_FILE = 'messages.json'
MAX_SIZE_MB = 100
LOCK = threading.Lock()

def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False)

def load_messages():
    ensure_data_file()
    with LOCK:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []

def save_messages(messages):
    with LOCK:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

def trim_if_too_large():
    size = os.path.getsize(DATA_FILE) / (1024*1024)
    if size > MAX_SIZE_MB:
        msgs = load_messages()
        keep = msgs[int(len(msgs)*0.1):]
        save_messages(keep)

@app.route('/')
def home():
    messages = list(reversed(load_messages()))
    return render_template('index.html', messages=messages)

@app.route('/add', methods=['POST'])
def add():
    data = request.get_json() or {}
    name = data.get('name', '').strip() or '匿名'
    msg = data.get('message', '').strip()
    if not msg:
        return jsonify({'error': '内容不能为空'}), 400
    messages = load_messages()
    messages.append({
        'name': name,
        'message': msg,
        'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    save_messages(messages)
    threading.Thread(target=trim_if_too_large).start()
    return jsonify({'ok': True})

if __name__ == '__main__':
    ensure_data_file()
    app.run(debug=True)