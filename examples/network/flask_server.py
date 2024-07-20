from flask import Flask, request, send_file
import maix # we do not use it but we import it to listening key event to exit this program

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def root():
    print("========")
    print(request.remote_addr)
    print(f'headers:\n{request.headers}')
    print(f'data: {request.data}')
    print("========")
    return 'hello world<br><img src="/img" style="background-color: black">'

@app.route("/<path:path>")
def hello(path):
    print(path)
    print(f'headers:\n{request.headers}')
    print(f'data: {request.data}')
    print("---------\n\n")
    return f"hello from {path}"

@app.route("/img")
def img():
    return send_file("/maixapp/share/icon/detector.png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

