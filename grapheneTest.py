import graphene

PATRONS = {
    '01': {
        "name": "Syrus",
        "age": 27
    }
}


class Patron(graphene.ObjectType):
    id = graphene.Field(graphene.ID)
    name = graphene.Field(graphene.String)
    age = graphene.Field(graphene.Int)

    def resolve_name(self, info):
        return PATRONS[self.id]['name']

    def resolve_age(self, info):
        return PATRONS[self.id]['age']

    def resolve_id(self, info):
        return self.id


class Query(graphene.ObjectType):

    patron = graphene.Field(Patron, id=graphene.ID(
        required=True,
    ))

    def resolve_patron(self, info, id):
        data = PATRONS[id]
        return Patron(id=id)


schema = graphene.Schema(query=Query)
query = '''
    query something($id: ID!){
      patron(id:$id) {
        id
        name
      }
    }
'''


def test_query():
    result = schema.execute(query, variable_values={'id': '01'})
    assert not result.errors
    assert result.data == {
        'patron': {
            'id': '1',
            'name': 'Syrus',
            'age': 27,
        }
    }


if __name__ == '__main__':
    result = schema.execute(query, variable_values={'id': '01'})
    if result.errors and len(result.errors) > 0:
        print(result.errors[0])
    print(result)
    print(result.data['patron'])
