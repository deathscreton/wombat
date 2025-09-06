#You will require the following libraries:
#flask, requests, logging

#You must enable Pangolin's API: https://docs.digpangolin.com/self-host/advanced/integration-api

########################################################################################################
# You must enable trust_proxy 1 in order to ensure Pangolin sanitizes the X-Forwarded-For header.      #
# Failure to do so can leave you vulnerable to spoofed headers!                                        #
# This is done by configuring "server:" under your config.yml.                                         #
# https://docs.digpangolin.com/self-host/advanced/config-file?utm_source=chatgpt.com#param-trust-proxy #
########################################################################################################


import requests, logging
from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix

session = requests.Session()

# Expected SHA256 fingerprint. Get it once with: openssl x509 -noout -fingerprint -sha256 -in pangolin_cert.pem/crt
# If you need your cert, you can extract it from /home/pangolin/config/letsencrypt using dumpcerts.traefik.v2.sh 
# You can locate that sh file online via it's github. It'll dump your certs as a crt. 
# Please note that this functionality isn't implemented yet. 
#EXPECTED_FP = "SHA56"
#session.mount("https://", FingerprintAdapter(EXPECTED_FP))

app = Flask(__name__)

#Configures request.remote_addr to look at X-Forwarded-For header instead of the forwarded IP which would most likely be Pangolin/whatever reverse proxy you have setup. 
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

#Block of code for logging purposes. 
handler = logging.FileHandler("flask.log")
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

@app.route("/")
def index():
    #checks (hopefully) sanitized X-Forwarded-For header for client IP address.
    visitor_ip = request.remote_addr
    #Requires an API key from Pangolin. See https://docs.digpangolin.com/manage/integration-api#api-key-types
    api_key = "api_key"
    #Leave the header as it is. Make sure to only change the api_key above. 
    headers = {"Authorization": f"Bearer {api_key}"}

    #Fetches rules. Change number after resource to resourceid of the resource you want to pull the rules for. 
    #ResourceID can be located by navigating to your Pang admin panel, selecting Resource, clicking edit on the resource you want the rules for, then finding the resource number in your URL. Make sure to also change 
    #"mydomain" to whatever domain you own and resourceid to match your resource in Pangolin. 
    response = session.get(url='https://api.mydomain.com/v1/resource/resourceid/rules?limit=1000&offset=0',headers=headers, )
    response.status_code
    app.logger.info(response.json())
    response_list = response.json()
    #Parses response_list for total rule count. 
    rule_total = response_list["data"]["pagination"]["total"]

    #parses response_list for IP addresses. 
    for rule in response_list["data"]["rules"]:
        rule_i = rule["value"]
        cur_rule = rule["ruleId"]
        app.logger.debug(f"rule_i: '{rule_i}'")
        if rule_i == visitor_ip:
           app.logger.warning(f"'{visitor_ip}' already exists in the database at ruleId'{cur_rule}'")
           app.logger.info(f"Total Rule Count: {rule_total}")
           ret = f"ALERT! <br>Your IP: '{visitor_ip}' is already registered with the Server! If you are having issues connecting with a mobile client, please doublecheck the server address and try again."
           return ret
        
    #Creates a new rule using PUT. Make sure to change "mydomain" to whatever domain you own and resourceid to match your resource in Pangolin. 
    response = session.put(url='https://api.mydomain.com/v1/resource/resourceid/rule/',headers=headers, json={"action": "ACCEPT","match": "IP","value": visitor_ip,"priority": 0,"enabled": True})
    app.logger.debug(response.json())
    res = f"Your IP: '{visitor_ip}'  has been processed. You should now have access to Jellyfin using a mobile application. If you change IPs (or location), you'll need to revisit this site again to re-register."
    rule_total = response_list["data"]["pagination"]["total"]
    app.logger.info(f"Total Rule Count: {rule_total}")
    return res

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

    #1212