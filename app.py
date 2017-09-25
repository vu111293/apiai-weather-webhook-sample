#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import os
import json
from collections import namedtuple
from flask import Flask, session
from flask import request
from flask import make_response

import uuid

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

activeUser = None
def processRequest(req):

    if not 'demo' in session:
        foo = Customer()
        session['demo'] = foo.toJson()
    else:
        js = session['demo']
        foo = Customer.fromJson(js)
        print(foo)


    action = req.get("result").get("action")
    parameters = req.get("result").get("parameters")

    if action == "userid":
        foo = Customer()
        foo.id = str(uuid.uuid4())
        # foo.name = parameters.get('name')
        foo.name = "Guest"
        session['demo'] = foo.toJson()
        return makeResponse(("Chào bạn. Rất vui được phục vụ bạn!"))

    elif action == "addproduct":
        productName = parameters.get("drink") 
        productAmount = parameters.get("number")

        product = Product()
        product.name = productName
        product.amount = productAmount
        cart = getattr(foo, 'cart', None)
        if cart is None:
            cart = []
        cart.append(product)
        foo.cart = cart
        session['demo'] = foo.toJson()
        return makeResponse(productName.encode('utf-8') + " được thêm vào giỏ hàng")

    elif action == 'viewcart':
        cart = getattr(foo, 'cart', None)
        if cart is None:
            print("Cart is empty")
            return makeResponse("Giỏ hàng rỗng!")
        else:
            dumps = "Giỏ hàng hiện tại có: "
            for item in cart:
                dumps += item.name.encode('utf-8') + ", "
                print("Product: " + item.name.encode('utf-8') + ": x" + str(item.amount).encode('utf-8'))
            return makeResponse(dumps)

    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

def makeResponse(msg):

    return {
        "speech": msg,
        "displayText": msg,
        "source": "innoway" 
    }


def cache(key, obj):
    session[key] = objectToJs(obj)

def getCache(key):
    if key in session:
        js = session[key]
        return jsToObject(js)
    return None

def jsToObject(data):
    return json.loads(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

def objectToJs(data):
    return json.dumps(data, default=lambda o: o.__dict__)


class Product(json.JSONEncoder):
    def default(self, o):
        return {'__{}__'.format(o.__class__.__name__): o.__dict__}

class Customer(json.JSONEncoder):
    def default(self, o):
        return {'__{}__'.format(o.__class__.__name__): o.__dict__}


    def toJson(self):
        return json.dumps(self, indent=4, cls=Customer)

    @staticmethod
    def fromJson(js):
        return json.loads(js, object_hook=decode_object)

def decode_object(o):
    if '__Customer__' in o:
        a = Customer()
        a.__dict__.update(o['__Customer__'])
        return a
    elif '__Product__' in o:
        a = Product()
        a.__dict__.update(o['__Product__'])
        return a
    return o
if __name__ == '__main__':
    # print (str(uuid.uuid4()))

    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(debug=False, port=port, host='0.0.0.0')

'''
    st = Customer()
    st.name = "MrVu"
    st.id = "12345"
    s10 = Product()
    s10.sr = 100
    st.score = s10
    js = st.toJson() # json.dumps(st, indent=4, cls=Customer)
    print(js)
    deserialized = Customer.fromJson(js) # json.loads(js, object_hook=decode_object)
    print(deserialized.name)

    # jsonobject = json.loads( str(js), object_hook= Foo)
    #jsonobject = Foo.fromJson(js)
    #print(jsonobject.haha)
   


    pass
    products = []
    products.append(Product("Cafe", 1))
    products.append(Product("Sinh to bo", 2))


    user = Customer()
    user.name = "Doan Ngoc Hai"
    user.cart = products


    del products[0]
    for p in products:
        print (p.name)
    

    # print(user.cart[1].number)
    print (len(products))
'''