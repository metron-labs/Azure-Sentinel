""" handles all DS api related functions """
import requests
import base64
from urllib.parse import urlparse

class api:

    def __init__(self, id, key, secret, url):
        """ 
            constructer initializes the DS creds and creates passkey.
            Parses the url recieved from user.
        """
        u = urlparse(url)

        self.url = "https://" + u.netloc + u.path + "/"
        passkey = key + ":" + secret
        self.id = id
        self.b64val = base64.b64encode(bytes(passkey, 'utf-8')).decode("ascii")

    def get_alerts(self, alert_id):
        """ 
            function for getting alerts using id
        """

        alert_url = self.url + "alerts?id=" + str(alert_id)
        response = requests.get(alert_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id})
        return response

    def get_incidents(self, incident_id):
        """ 
            function for getting incidents using id
        """
        
        incident_url = self.url + "incidents?id=" + str(incident_id)
        response = requests.get(incident_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id})
        return response

    def get_triage_events(self, before_date, after_date):
        """ 
            function for getting triage events,
            send only the DS converted dates using state serializer functions to get triage events
        """

        triage_url = self.url + "triage-item-events?event-created-before=" + str(before_date) + "&event-created-after=" +  str(after_date)
        response = requests.get(triage_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id})
        return response.text

    def get_triage_items(self, item_id_str):
        """  
            gets triage items from the triage events
        """
        
        items_url = self.url + "triage-items?id=" + str(item_id_str)
        response = requests.get(items_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id})
        return response.text

    def get_triage_comments(self, item_id_str):
        """  
            gets triage comments from the triage items
        """
        
        items_url = self.url + "triage-item-comments?id=" + str(item_id_str)
        response = requests.get(items_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id})
        return response.text