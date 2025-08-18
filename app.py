from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "mensaje": "Bienvenido a Visión vX.Ω",
        "estado": "OK",
        "version": "1.0.0"
    })

@app.route("/ping")
def ping():
    return jsonify({"respuesta": "pong"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
