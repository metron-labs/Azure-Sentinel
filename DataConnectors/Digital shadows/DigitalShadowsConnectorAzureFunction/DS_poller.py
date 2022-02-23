""" polls data from DS to azure logs """
import logging
from . import DS_api
from . import AS_api
from .state_serializer import State
import json
from . import constant
from DigitalShadowsConnectorAzureFunction import state_serializer

class poller:

    def __init__(self, ds_id, ds_key, secret, as_id, as_key, connection_string, historical_days, url):
        """ 
            initializes all necessary variables from other classes for polling 
        """
        
        self.DS_obj = DS_api.api(ds_id, ds_key, secret, url)
        self.AS_obj = AS_api.logs_api(as_id, as_key)
        self.date = State(connection_string)
        logging.info("got inside the poller code")
        self.event = self.date.get_last_event(historical_days)
        if(isinstance(self.event, tuple)):
            self.after_time = self.event[0]
            self.before_time = self.event[1]
            logging.info("From time: %s", self.after_time)
            logging.info("to time: %s", self.before_time)
        else:
            logging.info("Polling from event number " + str(self.event))

    def parse_desc(self, data):
        """
            adds more newlines to description for good display on Azure sentinel incidents
        """
        arr = data.splitlines()
        res = ""
        for e in arr:
            res = res + e + "\n\n"
        return res


    def post_azure(self, response, item):
        """
            posts to azure after appending triage information on it
        """
        json_obj = json.loads(response.text)
        for i in range(len(json_obj)):
            comment_data = json.loads(self.DS_obj.get_triage_comments(item[i]['id']))
            json_obj[i]['status'] = item[i]['state']
            json_obj[i]['triage_id'] = item[i]['id']
            json_obj[i]['triage_raised_time'] = item[i]['raised']
            json_obj[i]['triage_updated_time'] = item[i]['updated']
            
            comment_data_filtered = []
            for comment in comment_data:
                comment['user-name'] = comment['user']['name']
                del comment['triage-item-id']
                del comment['updated']
                del comment['user']
                if comment['content'] != "":
                    comment_data_filtered.append(comment)


            json_obj[i]['comments'] = comment_data_filtered
            
            json_obj[i]['description'] = self.parse_desc(json_obj[i]['description'])

            if('id' in json_obj[i] and not isinstance(json_obj[i]['id'], str)):
                json_obj[i]['description'] = json_obj[i]['description'] + "\n\nSearchlight Portal Link: https://portal-digitalshadows.com/triage/alert-incidents/" + str(json_obj[i]['id'])
        
            self.AS_obj.post_data(json.dumps(json_obj[i]), constant.LOG_NAME)

    def get_data(self):
        """
            getting the incident and alert data from digital shadows
        """
        triage_id = []
        try:
            if(isinstance(self.event, int)):
                event_dataJSON = self.DS_obj.get_triage_events_by_num(self.event)
                event_data = json.loads(event_dataJSON)
                #calculating the max event number from current batch to  use in next call
                max_event_num = max([e['event-num'] for e in event_data])
            else:
                event_dataJSON = self.DS_obj.get_triage_events(self.before_time, self.after_time)
                event_data = json.loads(event_dataJSON)
                #calculating the max event number from current batch to  use in next call
                max_event_num = max([e['event-num'] for e in event_data])
                logging.info("First poll from event number " + str(event_data[0]['event-num']))

            
            logging.info("total number of events are " + str(len(event_data)))
            
            for event in event_data:
                if(event is not None and event['triage-item-id'] not in triage_id):
                    triage_id.append(event['triage-item-id'])

            logging.info(triage_id)
        except (ValueError, IndexError, UnboundLocalError):            
            logging.info("JSON is of invalid format or no new incidents or alerts are found")
        
        item_data = json.loads(self.DS_obj.get_triage_items(triage_id))
        
        return item_data, max_event_num

    def poll(self):
        """
            main polling function, 
            makes api calls in following fashion:
            triage-events --> triage-items --> incidents and alerts 
        """
                    
        try:
            #sending data to sentinel
            inc_ids = []
            alert_ids = []
            item_data, max_event_num = self.get_data()
            logging.info("total number of items are " + str(len(item_data)))
            #creating list of ids by alert and incidents
            alert_triage_items = list(filter(lambda item: item['source']['alert-id'] is not None, item_data))
            inc_triage_items = list(filter(lambda item: item['source']['incident-id'] is not None, item_data))

            #getting data from DS and posting to Sentinel
            if inc_triage_items:
                inc_ids = [item['source']['incident-id'] for item in inc_triage_items]
                response = self.DS_obj.get_incidents(inc_ids)
                self.post_azure(response, inc_triage_items)
            if alert_triage_items:
                alert_ids = [item['source']['alert-id'] for item in alert_triage_items]
                response = self.DS_obj.get_alerts(alert_ids)    
                self.post_azure(response, alert_triage_items)

            #saving event num for next invocation
            self.date.post_event(max_event_num)
        except (KeyError, TypeError, UnboundLocalError, IndexError):
            logging.info("Key error or type error has occured or no new incidents or alerts are found")