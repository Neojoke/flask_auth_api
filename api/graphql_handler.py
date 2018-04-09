import graphene
from graphene.types import Scalar
from graphql.language import ast
import datetime
# 定义QL 枚举对象


class Episode(graphene.Enum):
    NEWHOPE = 4
    EMPIRE = 5
    JEDI = 6

    @property
    def description(self):
        if self == Episode.NEWHOPE:
            return "New Hope Episode"
        return "Other episode"

# 定义QL 自定义标量


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


# 定义QL 一个装载标量
class Person(graphene.ObjectType):
    name = graphene.Field(
        graphene.String, to=graphene.Argument(graphene.String))
    age = graphene.Int()

# #定义QL NonNull与List
# class Character(graphene.ObjectType):
#     name = graphene.String(required=True)
#     appears_in = graphene.List(graphene.List)

# 定义QL interface


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

# 定义QL AbstractTypes
# AbstractTypes包含可以在graphene.ObjectType,graphene.Interface,graphene.InputObjectType或者其他graphene.AbstractTypes共享的File字段


class UserFields(graphene.AbstractType):
    name = graphene.String()


class User(graphene.ObjectType, UserFields):
    pass


class UserInput(graphene.ObjectType, UserFields):
    pass

# 定义QL Unions 联合体类型非常像接口，但是他们不能指定类型之间任何共同的字段
# 每个Union 是一个Python继承graphene.Union的类
# 联合体没有任何属性在上面，仅链接可能的对象类型
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


# 定义QL ObjectTypes
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

# 定义QL schema
# schema是一种提供对每一种类型的操作的根类型，查询和更改(可选)，一个schema被定义以后交由validator和executor
# schema {
#     query: Query
#     mutation: Mutation
# }


# 定义QL Mutations
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

# 定义复杂QL 数组和单个对象
# type Todo{
#     task: String
#     description: String
# }
# type Todos{
#     tasks:[Todo]
# }


TODOS = {
    'todo1': {'task': 'build an API', 'description': "task1"},
    'todo2': {'task': '?????', 'description': "task2"},
    'todo3': {'task': 'profit!', 'description': "task3"},
}


class TodoTask(graphene.ObjectType):
    task_id = graphene.Field(graphene.String)
    task = graphene.Field(graphene.String)
    description = graphene.Field(graphene.String)

    def resolve_task(self, info):
        data = TODOS.get(self.task_id, None)
        return data['task']

    def resolve_description(self, info):
        data = TODOS.get(self.task_id, None)
        return data['description']


class createTodo(graphene.Mutation):
    class Arguments:
        task_id = graphene.String()
        task = graphene.String()
        description = graphene.String()
    ok = graphene.Boolean()
    todo = graphene.Field(lambda: TodoTask)

    def mutate(self, info, task_id, task, description):
        TODOS[task_id] = {"task": task, "description": description}
        ok = True
        todo = TodoTask(task_id=task_id, task=task, description=description)
        return createTodo(ok=ok, todo=todo)


class TodoMutations(graphene.ObjectType):
    create_todo = createTodo.Field()


class Query(graphene.ObjectType):
    # hello = graphene.String(name=graphene.String(default_value='stranger'))
    todo = graphene.Field(
        TodoTask, task_id=graphene.String(
            required=True,
        ))

    # def resolve_hello(self, info, name):
    #     print("info is : %s", (info,))
    #     print("name is : %s", (name,))
    #     return "Hello " + name

    def resolve_todo(self, info, task_id):
        todo = TodoTask(task_id=task_id)
        todo.task_id = task_id
        return todo


schema = graphene.Schema(query=Query, mutation=TodoMutations)

queryTodo = '''
    query getTodo($taskId: String!){
      todo(taskId:$taskId) {
        task
        description
      }
    }
'''

mutationTodo = '''
    mutation createTodo { 
        createTodo(taskId:"task4",task:"do something",description:"no.4") { 
            todo { 
                task 
                description 
            } 
            ok 
        } 
    }
'''


def handle_ql(ql, variable_values=None):
    result = schema.execute(ql, variable_values=variable_values)
    return result


# if __name__ == '__main__':
#     result = handle_ql(mutationTodo, {})
#     if result.errors and len(result.errors) > 0:
#         print(result.errors[0])
#     print(result)
#     print(result.data)
