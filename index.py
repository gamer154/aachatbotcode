import requests
import time

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    return  "Hello there my friend !!"
	
@app.route('/static_reply', methods=['POST'])
def static_reply():
    speech = "Hello there, this reply is from the webhook !! "
    string = "You are awesome !!"
    Message ="this is the message"

    my_result =  {

    "fulfillmentText": string,
     "source": string
    }

    res = json.dumps(my_result, indent=4)

    r = make_response(res)

    r.headers['Content-Type'] = 'application/json'
    return r
	
@app.route('/snow_request', methods=['POST'])
def snow_request():
    req = request.get_json(silent=True, force=True)
    if req.get("queryResult").get("action") == "input.CreateIncidentSNOW":
        shortdescription = req.get("queryResult").get("parameters").get("short_description")
        r = createticket(shortdescription)
        return r
    if req.get("queryResult").get("action") == "input.CheckSNOWStatus":
        id = req.get("queryResult").get("parameters").get("id")
        r = checkstatus(id)
        return r

def CRauth():
    authurl = "<enter url>"
    data = {"Username": "<user>","Password": "<password>"}
    data_json = json.dumps(data)
    headers = {'Content-Type':'application/json'}
    response = requests.post(authurl, data=data_json, headers=headers)
    output = response.json()
    token = output['token']
    return token

def addsnowqWI(workitem): 
    token = CRauth()
    crqurl = "http://cf433f1d.ngrok.io/v1/wlm/queues/6/workitems"
    data = {"test":workitem}
    data_json = json.dumps(data)
    headers = {"Content-Type":"application/json","X-Authorization":token}
    response = requests.post(crqurl, data=data_json, headers=headers)
    output = response.json()
    id = output[0]['id']
    return id

def getsnowqWI(id):
    token = CRauth()
    crqurl = "http://cf433f1d.ngrok.io/v1/wlm/queues/6/workitems/list"
    data = {"sort":[],"filter":{"operator":"or","operands":[{ "field":"id", "operator": "eq", "value":id}]},"fields":[],"page":{"length": 200,"offset": 0}}
    data_json = json.dumps(data)
    headers = {"Content-Type":"application/json","X-Authorization":token}
    response = requests.post(crqurl, data=data_json, headers=headers)
    output = response.json()
    getsnowqWI.status = output['list'][0]['status']
    getsnowqWI.result = output['list'][0]['result']

def slackmsg(msg):
    slackhook = "https://hooks.slack.com/services/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"
    data = {"text": msg}
    data_json = json.dumps(data)
    headers = {'Content-Type':'application/json'}
    response = requests.post(slackhook, data=data_json, headers=headers)

def snowdirectpost(description):
    snowurl = "https://dev69254.service-now.com/api/now/v1/table/incident"
    data = {"short_description":shortdescription,"comments":"chatbot executing"}
    data_json = json.dumps(data)
    headers = {'Content-Type':'application/json','Authorization':'Basic YWRtaW46Tmltc29mdDEyMw=='}
    response = requests.post(snowurl, data=data_json, headers=headers)
    output = response.json()
    incinum = output['result']['number']
    outputreply = "You're incident number is "
    reply = outputreply+incinum
    return reply
	
def createticket(shortdescription):
    workitemID = addsnowqWI(shortdescription)
    getsnowqWI(workitemID)
    WIstatus = getsnowqWI.status
    reply = "Processing your request. You're workitem ID is "+str(workitemID)+". Current status of your request is "+WIstatus+". If you do not receive another response in an minute. Please type: check status of "+str(workitemID)+"."
    my_result = {
        "fulfillmentText": reply,
        "source": reply
        }
    res = json.dumps(my_result, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
	
def checkstatus(id):
    getsnowqWI(id)
    status = getsnowqWI.status
    result = getsnowqWI.result 
    if status == "COMPLETED":
        reply = "You're ticket has been created. Here is the result: \n"+result
    else:
        reply = "You're ticket is still being created. Status is: "+status
    my_result = {
        "fulfillmentText": reply,
        "source": reply
        }
    res = json.dumps(my_result, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
	
if __name__ == "__main__":
	port = int(os.getenv('PORT', 5000))
	print("Starting app on port %d" % port)
	app.run(debug=True, port=port, host='0.0.0.0')