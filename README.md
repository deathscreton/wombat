# wombat
Wombat is a small python script used to semi-integrate Pangolin SSO with services that aren't directly compatible
without having to disable Pangolin's native auth, or install any separate auth software like OID or Authentik. 

# What does this mean?
Let's use a real world example. 

Jellyfin is a popular media server software. It has a native mobile app as well. Pangolin, when exposing services
to the internet uses a redirect to push browsers to an authentication page. This works fine so long as you're using a 
browser, but the mobile clients for Jellyfin cannot handle this redirect. 

In comes Wombat. Wombat acts as a intermediary between Pangolin's SSO and the service you'd like to expose. 
It does this by utilizing Python, flask, and requests to call Pangolin's API to modify rules belonging
to the service in question when a person navigates to the flask hosted endpoint in a web browser. 
Once a user accesses this endpoint and provides Pangolin with whatever information it requests to allow access,
the user will hit the web service. The python script collects the user's IP address, fetches the rule list for
the resource of your choice, checks it for the IP of the user, then either rejects the change if it already exists
or creates a new bypass rule for the IP in question. This effectively turns off Pangolin authentication for that IP
while the rule exists. At this point, the user then can return to Jellyfin's mobile app and log into the service. 

# Can I only use it with Pangolin or Jellyfin? 
Wombat is designed in a way where it is both service and even proxy agnostic. Since Wombat does not directly interface
with anything besides Pangolin's API, you are responsible for supplying this information if you are not utilizing Pangolin. 

# Usage
Before you can utilize Wombat, you must have the met the following prerequisites:

Download the following python libraries to whatever server you're using. It goes without saying that you'll also
python on this server as well: flask, requests, logging

You must enable Pangolin's API to expose the API endpoint: https://docs.digpangolin.com/self-host/advanced/integration-api
You'll also need to generate an API key for your usage: https://docs.digpangolin.com/manage/integration-api#api-key-types

########################################################################################################
 You must enable trust_proxy 1 in order to ensure Pangolin sanitizes the X-Forwarded-For header.      
 Failure to do so can leave you vulnerable to spoofed headers!                                        
 This is done by configuring "server:" under your config.yml.                                         
 https://docs.digpangolin.com/self-host/advanced/config-file?param-trust-proxy
########################################################################################################
