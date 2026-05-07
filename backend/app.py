from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/api/health")
def health_check():
    return jsonify({
        "status": "ok",
        "message": "backend is running",
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
