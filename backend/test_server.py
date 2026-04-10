from flask import Flask
from config import config

app = Flask(__name__)
app.config.from_object(config['development'])

@app.route('/')
def test():
    return '<h1>Server Running!</h1><p>Backend OK. Go to <a href="/admin">Admin Panel</a></p>'

if __name__ == '__main__':
    print("TEST SERVER - Port 5000")
    app.run(debug=True, port=5000)
