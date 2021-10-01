""" polls data from DS to azure logs """
import logging
from . import DS_api
from . import AS_api
from .state_serializer import State
import json
from . import constant

class poller:

    def __init__(self, ds_id, ds_key, secret, as_id, as_key, connection_string, historical_days):
        """ 
            initializes all necessary variables from other classes for polling 
        """
        
        self.DS_obj = DS_api.api(ds_id, ds_key, secret)
        self.AS_obj = AS_api.logs_api(as_id, as_key)
        date = State(connection_string)
        logging.info("got inside the poller code")
        self.after_time, self.before_time = date.get_last_polled_time(historical_days)
        logging.info("From time: %s", self.after_time)
        logging.info("to time: %s", self.before_time)

    def poll(self):
        """
            main polling function, 
            makes api calls in following fashion:
            triage-events --> triage-items --> incidents and alerts 
        """
        
        try:
            event_dataJSON = self.DS_obj.get_triage_events(str(self.before_time), str(self.after_time))
            event_data = json.loads(event_dataJSON)
            for event in event_data:            
                item_data = json.loads(self.DS_obj.get_triage_items(event['triage-item-id']))
                    
                #sending data to sentinel
                for item in item_data:
                    if(item['source']['incident-id'] is not None):
                        response = self.DS_obj.get_incidents(item['source']['incident-id'])
                        self.AS_obj.post_data(json.dumps(response.json()), constant.LOG_NAME)

                    if(item['source']['alert-id'] is not None):
                        response = self.DS_obj.get_alerts(item['source']['alert-id'])
                        self.AS_obj.post_data(json.dumps(response.json()), constant.LOG_NAME)
        except ValueError:
            logging.info("JSON is of invalid format")
