""" polls data from DS to azure logs """
import logging
from . import DS_api
from . import AS_api
from .state_serializer import State
import json
from . import constant

class poller:

    def __init__(self, ds_id, ds_key, secret, as_id, as_key, connection_string, historical_days, url):
        """ 
            initializes all necessary variables from other classes for polling 
        """
        
        self.DS_obj = DS_api.api(ds_id, ds_key, secret, url)
        self.AS_obj = AS_api.logs_api(as_id, as_key)
        date = State(connection_string)
        logging.info("got inside the poller code")
        self.after_time, self.before_time = date.get_last_polled_time(historical_days)
        logging.info("From time: %s", self.after_time)
        logging.info("to time: %s", self.before_time)

    def post_comments(self, comment):
        self.AS_obj.post_data(json.dumps(comment), constant.COMMENTS_LOG_NAME)


    def post_azure(self, response, item):
        """
            posts to azure after appending triage information on it
        """
        json_obj = json.loads(response.text)
        json_obj[0]['status'] = item['state']
        json_obj[0]['triage_id'] = item['id']
        json_obj[0]['triage_raised_time'] = item['raised']
        json_obj[0]['triage_updated_time'] = item['updated']
        self.AS_obj.post_data(json.dumps((json_obj[0])), constant.LOG_NAME)

    def poll(self):
        """
            main polling function, 
            makes api calls in following fashion:
            triage-events --> triage-items --> incidents and alerts 
        """
        
        try:
            event_dataJSON = self.DS_obj.get_triage_events(str(self.before_time), str(self.after_time))
            event_data = json.loads(event_dataJSON)
            
            triages_str = str(event_data[0]['triage-item-id'])
            for event in event_data:
                #logging.info(event)
                if(event is not None):
                    triages_str = triages_str + "&id=" + str(event['triage-item-id'])

        except (ValueError, IndexError):
            logging.info("JSON is of invalid format or no new incidents or alerts are found")

        try:
            item_data = json.loads(self.DS_obj.get_triage_items(triages_str))
            comments = json.loads(self.DS_obj.get_triage_comments(triages_str))
        except UnboundLocalError:
            logging.info("No new incidents or alerts found")
                    
        try:
            #sending data to sentinel
            for item in item_data:
                if(item['source']['incident-id'] is not None):
                    response = self.DS_obj.get_incidents(item['source']['incident-id'])
                    self.post_azure(response, item)

                elif(item['source']['alert-id'] is not None):
                    response = self.DS_obj.get_alerts(item['source']['alert-id'])
                    self.post_azure(response, item)
            
            for c in comments:
                self.post_comments(c)


        except (KeyError, TypeError, UnboundLocalError):
            logging.info("Key error or type error has occured or no new incidents or alerts are found")