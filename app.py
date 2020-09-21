from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required

from security import authenticate, identify

app = Flask(__name__)
app.secret_key = 'ghjinl'
api = Api(app)
jwt = JWT(app, authenticate, identify)

items = []

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help='This field cannot be left!')
    @jwt_required()   # /auth -- end point
    def get(self, name):
        item = next(filter(lambda x: x['name'] == name, items), None)
        return {'items': item}, 200 if item else 404

    def post(self, name):
        if next(filter(lambda x: x['name'] == name, items), None):  # 400
            return {'message': "Item '{}' is already existed".format(name)}

        request_data = request.get_json()
        post_item = {'name': name, 'price': request_data['price']}
        items.append(post_item)
        return post_item, 201

    def put(self, name):
        data = Item.parser.parse_args()  # using parser format 
        put_item = next(filter(lambda x: x['name'] == name, items), None)
        if put_item is None:
            put_item = {'name': name, 'price': data['price']}
            items.append(put_item)
        else:
            put_item.update(data)
        return put_item


    def delete(self, name):
        global items
        items = list(filter(lambda x: x['name'] != name, items))
        return {'message': "Item '{}' deleted".format(name)}

class ItemList(Resource):
    def get(self):
        return {'items': items}  # providing all the items list


api.add_resource(ItemList, '/items')
api.add_resource(Item, '/item/<string:name>')


if __name__ == "__main__":
    app.run(port=5000, debug=True)
