""" handles all DS api related functions """
import logging
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

    def get_alerts(self, alert_ids):
        """ 
            function for getting alerts using id
        """

        alert_id_str = alert_ids[0]
        for ele in alert_ids[1:]:
            alert_id_str = alert_id_str + "&id=" + ele

        alert_url = self.url + "alerts?limit=20&id=" + str(alert_id_str)
        response = requests.get(alert_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id, "User-Agent": "DigitalShadowsAzureSentinelIntegration"})
        logging.info("Alerts response code: %s" % response.status_code)
        return response

    def get_incidents(self, incident_ids):
        """ 
            function for getting incidents using id list
        """
        
        inc_id_str = str(incident_ids[0])
        for ele in incident_ids[1:]:
            inc_id_str = inc_id_str + "&id=" + str(ele)

        incident_url = self.url + "incidents?limit=20&id=" + inc_id_str
        response = requests.get(incident_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id})
        logging.info("Incident response code: %s" % response.status_code)
        return response

    def get_triage_events(self, before_date, after_date):
        """ 
            function for getting triage events,
            send only the DS converted dates using state serializer functions to get triage events
        """

        triage_url = self.url + "triage-item-events?limit=20&event-created-before=" + str(before_date) + "&event-created-after=" +  str(after_date)
        response = requests.get(triage_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id})
        logging.info("Events response code: %s" % response.status_code)
        return response.text

    def get_triage_items(self, triage_ids):
        """  
            gets triage items from the triage events
        """

        item_id_str = triage_ids[0]
        for ele in triage_ids[1:]:
            item_id_str = item_id_str + "&id=" + ele

        items_url = self.url + "triage-items?limit=20&id=" + item_id_str
        response = requests.get(items_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id})
        logging.info("Triage items response code: %s" % response.status_code)
        return response.text

    def get_triage_comments(self, item_id):
        """  
            gets triage comments from the triage items
        """

        items_url = self.url + "triage-items/" + str(item_id) + "/comments"
        response = requests.get(items_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id})
        logging.info("Comments response code: %s" % response.status_code)
        return response.text
    
    def get_triage_events_by_num(self, event):
        """
            gets triage events by number
        """
        triage_url = self.url + "triage-item-events?limit=20&event-num-after=" + str(event)
        response = requests.get(triage_url, headers={"Authorization": "Basic %s" % self.b64val, "searchlight-account-id": "%s" % self.id})
        logging.info("Events by num %d response code: %s" % (event, response.status_code))
        return response.text
