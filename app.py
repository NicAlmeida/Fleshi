from flask import Flask, render_template, request


app = Flask(__name__)

@app.route('/')
def homepage():
    return "Rede social de fotos - Fleshi"


if __name__ == '__main__':
    app.run(debug=True)

