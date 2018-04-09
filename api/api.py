from flask import Blueprint, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with

import datetime
from api.graphql_handler import handle_ql
import json

api_app = Blueprint("api", __name__)
api_app.register_error_handler
restful_api = Api(api_app)


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist.".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument('task', action='append')
parser.add_argument('description')
resource_fields = {
    'name': fields.String,
    'address': fields.String,
    'date_updated': fields.DateTime(dt_format='rfc822'),
}


TODOS = {
    'todo1': {'task': 'build an API', 'description': "task1"},
    'todo2': {'task': '?????', 'description': "task2"},
    'todo3': {'task': 'profit!', 'description': "task3"},
}


class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {"task": args['task'], "description": args["description"]}
        TODOS[todo_id] = task
        return task, 201


class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        from_idx = int(max(TODOS.keys()).lstrip('todo'))
        result = {}
        idx = 0
        for task in args['task']:
            todo_id = 'todo%i' % (from_idx+idx+1)
            TODOS[todo_id] = {'task': task}
            result[todo_id] = {'task': task}
            idx += 1
        return result, 201


restful_api.add_resource(TodoList, "/todos")
restful_api.add_resource(Todo, '/todos/<todo_id>')


ql_parser = reqparse.RequestParser()
ql_parser.add_argument('query', type=str)
ql_parser.add_argument('operationName', type=str, required=False)
ql_parser.add_argument('variables', required=False)


class graph_ql(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        ql_str = json_data['query']
        variable_values = json_data.get('variables', None)
        print(ql_str)
        result = handle_ql(ql_str, variable_values)
        print(result)
        if result.errors and len(result.errors) > 0:
            print(result.errors)
        return result.data, 200


restful_api.add_resource(graph_ql, "/ql")
