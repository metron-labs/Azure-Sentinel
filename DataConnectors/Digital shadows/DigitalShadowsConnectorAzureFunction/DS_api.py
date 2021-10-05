""" handles all DS api related functions """
import requests
import base64


class api:
    
    url = "https://api.searchlight.app/v1/"                 #main url for api

    """ constructer initializes the DS creds """
    def __init__(self, id, key, secret):
        passkey = key + ":" + secret
        self.id = id
        self.b64val = base64.b64encode(bytes(passkey, 'utf-8')).decode("ascii")

    def get_alerts(self, alert_id):
        alert_url = self.url + "alerts?id=" + str(alert_id)
        response = requests.get(alert_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id})
        return response

    def get_incidents(self, incident_id):
        incident_url = self.url + "incidents?id=" + str(incident_id)
        response = requests.get(incident_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id})
        return response

    """ send only the DS converted dates using state serializer functions """
    def get_triage_events(self, before_date, after_date):
        triage_url = self.url + "triage-item-events?event-created-before=" + str(before_date) + "&event-created-after=" +  str(after_date)
        response = requests.get(triage_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id})
        return response.text

    def get_triage_items(self, item_id):
        items_url = self.url + "triage-items?id=" + str(item_id)
        response = requests.get(items_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id})
        return response.text