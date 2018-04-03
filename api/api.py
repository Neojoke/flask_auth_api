from flask import Blueprint, request

api_app = Blueprint("api", __name__)


@api_app.route("/index")
def index():
    print(request.args)
    return "hello"
