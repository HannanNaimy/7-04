from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

@app.route("/")
def guest():
    return render_template("guest.html")

if __name__ == "__main__":
    app.run()
