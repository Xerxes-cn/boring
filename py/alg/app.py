from pprint import pprint

from flask import Flask
from flask import g
from flask import current_app
from flask .helpers import find_package

app = Flask(__name__)
# pprint(app.request_class)
print(__name__)
print(find_package(__name__))


@app.route("/")
def index():
    # pprint(request.environ.get("flask._preserve_context"))
    # pprint(current_app.preserve_context_on_exception)
    pprint(type(g))
    return {}


if __name__ == '__main__':
    app.run(debug=True)
