#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask, session
from flask import request
from flask import make_response

from user import Customer
from user import Product
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
    if "global-user" in session:
        activeUser = session["global-user"]
    action = req.get("result").get("action")
    parameters = req.get("result").get("parameters")


    if action == "user_identify":
        activeUser = Customer()
        activeUser.id = uuid.uuid4()
        session["global-user"] = activeUser.__dict__
        return makeResponse("Hello user  " + str(activeUser.id))

    elif action == "add_product":
        productName = parameters.get("product-name") 
        productAmount = parameters.get("product-amount")

        product = Product(productName, productAmount)
        if hasattr(activeUser, "cart") == False:
            activeUser.cart = []
        activeUser.cart.append(product)

        session["global-user"] = activeUser
        return makeResponse(productName + " added!")


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



if __name__ == '__main__':
    # print (str(uuid.uuid4()))
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(debug=False, port=port, host='0.0.0.0')

'''
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