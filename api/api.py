from flask import Blueprint, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
import graphene
from graphene.types import Scalar
from graphql.language import ast
import datetime

api_app = Blueprint("api", __name__)
api_app.register_error_handler
restful_api = Api(api_app)

TODOS = {
    'todo1': {'task': 'build an API','description':"task1"},
    'todo2': {'task': '?????','description':"task2"},
    'todo3': {'task': 'profit!','description':"task3"},
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

#定义QL 枚举对象
class Episode(graphene.Enum):
    NEWHOPE = 4
    EMPIRE = 5
    JEDI = 6
    @property
    def description(self):
        if self == Episode.NEWHOPE:
            return "New Hope Episode"
        return "Other episode"

#定义QL 自定义标量
class DateTime(Scalar):
    '''DateTime Scalar Description'''
    @staticmethod
    def serialize(dt):
        return dt.isoformat()

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return datetime.datetime.strptime(
                node.value, "%Y-%m-%dT%H:%M:%S.%f")

    @staticmethod
    def parse_value(value):
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
    

#定义QL 一个装载标量
class Person(graphene.ObjectType):
    name = graphene.Field(graphene.String, to=graphene.Argument(graphene.String))
    age = graphene.Int()

# #定义QL NonNull与List
# class Character(graphene.ObjectType):
#     name = graphene.String(required=True)
#     appears_in = graphene.List(graphene.List)

#定义QL interface
class Character(graphene.Interface):
    name = graphene.String()

# Human is a charater implementation
class Human(graphene.ObjectType):
    class Meta:
        interfaces = (Character,)
    born_in = graphene.String()

# Droid is a Character implementation
class Droid(graphene.ObjectType):
    class Meta:
        interfaces = (Character,)
    function = graphene.String()

class Straship(graphene.ObjectType):
    class Meta:
        interfaces = (Character,)
    length = graphene.Int()

#定义QL AbstractTypes
#AbstractTypes包含可以在graphene.ObjectType,graphene.Interface,graphene.InputObjectType或者其他graphene.AbstractTypes共享的File字段
class UserFields(graphene.AbstractType):
    name = graphene.String()

class User(graphene.ObjectType, UserFields):
    pass

class UserInput(graphene.ObjectType, UserFields):
    pass

#定义QL Unions 联合体类型非常像接口，但是他们不能指定类型之间任何共同的字段
#每个Union 是一个Python继承graphene.Union的类
#联合体没有任何属性在上面，仅链接可能的对象类型
# type Droid {
#     name: String
#     function: String
# }
# type Human {
#     name: String
#     born_in: String 
# }
# type Ship{
#     name: String
#     length: Int
# }
# union SearchResult = Human | Droid | Starship

class SearchResult(graphene.Union):
    class Meta:
        types = (Human, Droid, Straship)


#定义QL ObjectTypes
# type Player{
#     firstName: String
#     lastName: String
#     fullName: String
# }
class Player(graphene.ObjectType):
    first_name = graphene.String()
    last_name = graphene.String()
    full_name = graphene.String()

    def resolve_full_name(self, info):
        return '{} {}'.format(self.first_name, self.last_name)

#定义QL schema
# schema是一种提供对每一种类型的操作的根类型，查询和更改(可选)，一个schema被定义以后交由validator和executor
# schema {
#     query: Query
#     mutation: Mutation
# } 


#定义QL Mutations
class CreatePerson(graphene.Mutation):
    class Arguments:
        name = graphene.String()
    ok = graphene.Boolean()
    person = graphene.Field(lambda: Person)
    def mutate(self, info, name):
        person = Person(name)
        ok = True
        return CreatePerson(person=person, ok=ok)

class MyMutations(graphene.ObjectType):
    create_person = CreatePerson.Field()

#定义复杂QL 数组和单个对象
# type Todo{
#     task: String
#     description: String
# }
# type Todos{
#     tasks:[Todo]
# }

class TodoTask(graphene.ObjectType):
    task = graphene.String()
    description = graphene.String()
    def resolve_task(self, info, task_id):
        print('task property')
        print(info)
        print(task_id)
        return TODOS.get(task_id, None).get('task',None)
    def resolve_description(self, info, task_id):
        print('description property')
        print(info)
        print(task_id)
        return TODOS.get(task_id, None).get('description',None)
            
class TodoTaks(graphene.ObjectType):
    tasks = graphene.List(graphene.Field(TodoTask))

class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value='stranger'))
    person = graphene.Field(Person)
    todo = graphene.Field(TodoTask, task_id=graphene.String(default_value=None))
    def resolve_hello(self, info, name):
        print ("info is : %s", (info,))
        print("name is : %s",(name,))
        return "Hello " + name


schema = graphene.Schema(query=Query,types=None, mutation=MyMutations)

ql_parser = reqparse.RequestParser()
ql_parser.add_argument('query', type=str)
ql_parser.add_argument('operationName', type=str, required=False)
ql_parser.add_argument('variables', required=False)

class graph_ql(Resource):
    def post(self):
        ql_str = ql_parser.parse_args()['query']
        variable_values = ql_parser.parse_args()['variables']
        print(ql_str)
        result = schema.execute(ql_str, variable_values=variable_values)
        print(result)
        if result.errors and len(result.errors) > 0:
            print(result.errors)
        return result.data, 200


restful_api.add_resource(graph_ql, "/ql")
