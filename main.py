from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def mission_page():
    return render_template('basic_template.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')