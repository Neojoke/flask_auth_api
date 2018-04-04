from flask import Blueprint, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
import graphene

api_app = Blueprint("api", __name__)
api_app.register_error_handler
restful_api = Api(api_app)

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist.".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument('task', action='append')
resource_fields = {
    'name': fields.String,
    'address': fields.String,
    'date_updated': fields.DateTime(dt_format='rfc822'),
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
        task = {"task": args['task']}
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


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value='stranger'))

    def resolve_hello(self, info, name):
        return "Hello " + name


schema = graphene.Schema(query=Query)

ql_parser = reqparse.RequestParser()
ql_parser.add_argument('query', type=str)
ql_parser.add_argument('operationName', type=str, required=False)
ql_parser.add_argument('variables', required=False)


class graph_ql(Resource):
    def post(self):
        ql_str = ql_parser.parse_args()['query']
        print(ql_str)
        result = schema.execute(ql_str)
        return schema.execute(ql_str).data, 200


restful_api.add_resource(graph_ql, "/ql")
