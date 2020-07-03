from flask import Flask
from flask_restful import Resource, Api
from Cart import Cart
from Item import Item
import paho.mqtt.client as mqtt
import threading
import json
from Path import Path
from XMLParsar import XMLParser
import xml.etree.ElementTree as ElementTree

app = Flask(__name__)
api = Api(app)


class ItemCount(Resource):
    def get(self, itemNum):
        itemRoot = ElementTree.parse("Items.xml").getroot()
        itemQuery = ".//Item[@itemNum='" + str(itemNum) + "']"
        int(itemRoot.find(itemQuery).get('count'))
        return {int(itemRoot.find(itemQuery).get('name')) : int(itemRoot.find(itemQuery).get('count'))}, 200


class CartAssign(Resource):
    def get(self, cartNum):
        cartRoot = ElementTree.parse("Carts.xml").getroot()
        cartQuery = ".//Cart[@itemNum='" + str(cartNum) + "']"
        if cartRoot.find(cartQuery).get('isAssigned') == "False":
            cartRoot.find(cartQuery).set('isAssigned', 'True')
            XMLParser.getInstance().writeAndPretify(cartRoot, "Carts.xml")
            return 200
        else:
            return 404


class CartUnAssign(Resource):
    def get(self, cartNum):
        cartRoot = ElementTree.parse("Carts.xml").getroot()
        cartQuery = ".//Cart[@itemNum='" + str(cartNum) + "']"
        cartRoot.find(cartQuery).set('isAssigned', 'False')
        XMLParser.getInstance().writeAndPretify(cartRoot, "Carts.xml")
        return 200


class IsPathOccupied(Resource):
    def get(self, fromX, fromY, toX, toY):
        pathRoot = ElementTree.parse("Paths.xml").getroot()
        pathQuery = ".//Cart[@fromX='" + fromX + "'][@fromY='" + fromY + "'][@toX='" + toX + "'][@toY='" + toY + "']"
        if pathRoot.find(pathQuery).get("isPathOccupied") == "False":
            return 200
        else:
            return 404


@app.route('/')
def hello_world():
    return 'Hello World!'


api.add_resource(CartAssign, '/getCart/<int:cartNum>')
api.add_resource(ItemCount, '/getItemCount/<int:itemNum>')
api.add_resource(CartUnAssign, '/giveCart/<int:cartNum>')
api.add_resource(IsPathOccupied, '/isPathOccupied/<int:fromX>/<int:fromY>/<int:toX>/<int:toY>')


if __name__ == '__main__':

    items = Item()
    carts = Cart()
    paths = Path()

    itemRoot = ElementTree.parse("Items.xml").getroot()
    cartRoot = ElementTree.parse("Carts.xml").getroot()
    pathRoot = ElementTree.parse("Paths.xml").getroot()

    def on_message(client, userdata, message):

        if message.topic == 'item/':
            messageJson = json.loads(message.payload.decode())
            itemPurchased = messageJson["itemPurchased"]

            itemRoot = ElementTree.parse("Items.xml").getroot()
            itemQuery = ".//Item[@name='" + itemPurchased + "']"
            currCount = int(itemRoot.find(itemQuery).get('count')) - 1
            itemRoot.find(itemQuery).set('count', str(currCount))
            XMLParser.getInstance().writeAndPretify(itemRoot, "Items.xml")

        if message.topic == 'pathOccupy/':
            messageJson = json.loads(message.payload.decode())
            fromX = messageJson["fromx"]
            fromY = messageJson["fromy"]
            toX = messageJson["tox"]
            toY = messageJson["toy"]

            pathRoot = ElementTree.parse("Paths.xml").getroot()
            pathQuery = ".//Cart[@fromX='" + fromX + "'][@fromY='" + fromY + "'][@toX='" + toX + "'][@toY='" + toY + "']"
            pathRoot.find(pathQuery).set("isPathOccupied", "True")
            pathQuery = ".//Cart[@fromX='" + toX + "'][@fromY='" + toY + "'][@toX='" + fromX + "'][@toY='" + fromY + "']"
            pathRoot.find(pathQuery).set("isPathOccupied", "True")
            XMLParser.getInstance().writeAndPretify(pathRoot, "Paths.xml")

        if message.topic == 'pathUnoccupy/':
            messageJson = json.loads(message.payload.decode())
            fromX = messageJson["fromx"]
            fromY = messageJson["fromy"]
            toX = messageJson["tox"]
            toY = messageJson["toy"]

            pathRoot = ElementTree.parse("Paths.xml").getroot()
            pathQuery = ".//Cart[@fromX='" + fromX + "'][@fromY='" + fromY + "'][@toX='" + toX + "'][@toY='" + toY + "']"
            pathRoot.find(pathQuery).set("isPathOccupied", "False")
            pathQuery = ".//Cart[@fromX='" + toX + "'][@fromY='" + toY + "'][@toX='" + fromX + "'][@toY='" + fromY + "']"
            pathRoot.find(pathQuery).set("isPathOccupied", "False")
            XMLParser.getInstance().writeAndPretify(pathRoot, "Paths.xml")


    def startLooping():
        mqtt_subscriber.loop_forever()


    mqtt_subscriber = mqtt.Client('item tracking receiver')
    mqtt_subscriber.on_message = on_message
    mqtt_subscriber.connect('192.168.0.104', 1883, 70)
    mqtt_subscriber.subscribe('item/', 2)
    mqtt_subscriber.subscribe('pathOccupy/', 2)
    mqtt_subscriber.subscribe('pathUnoccupy/', 2)

    thread = threading.Thread(target=startLooping)
    thread.start()

    app.run(host='0.0.0.0')