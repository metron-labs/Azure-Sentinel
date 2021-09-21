#polls data from DS to azure logs
from . import DS_api
from . import AS_api
from . import state_serializer
import json

class poller:
    log_type = 'InALogs'                    #custom logs name

    def __init__(self, ds_id, ds_key, secret, as_id, as_key):
        self.DS_obj = DS_api.api(ds_id, ds_key, secret)
        self.AS_obj = AS_api.logs_api(as_id, as_key)
        self.date = state_serializer.state()
        self.date.get_last_updated()

    def get_new_time(self, response):
        curr_event_list = json.loads(response.text)
        curr_event = curr_event_list[0]
                    
        if(curr_event['updated'] is not None):                       #first element of the list is the json dictionary
            curr_time = state_serializer.state.convert_to_datetime(curr_event['updated'])
            if(self.date.after_time < curr_time):
                self.date.after_time = curr_time
        else:
            curr_time = state_serializer.state.convert_to_datetime(curr_event['raised'])
            if(self.date.after_time < curr_event):
                self.date.after_time = curr_time


    def poll(self):
        day = self.date.before_time.strftime("%Y-%m-%d")
        hour = self.date.before_time.strftime("%H")
        minute = self.date.before_time.strftime("%M")
        second = self.date.before_time.strftime("%S")

        day_after = self.date.after_time.strftime("%Y-%m-%d")
        hour_after = self.date.after_time.strftime("%H")
        minute_after = self.date.after_time.strftime("%M")
        second_after = self.date.after_time.strftime("%S")

        event_data = json.loads(self.DS_obj.get_triage_events(state_serializer.state.convert_to_DS_time(day, hour, minute, second), state_serializer.state.convert_to_DS_time(day_after, hour_after, minute_after, second_after)))
        
        for event in event_data:            
            item_data = json.loads(self.DS_obj.get_triage_items(event['triage-item-id']))
            
            #sending data to sentinel
            for item in item_data:
                if(item['source']['incident-id'] is not None):
                    response = self.DS_obj.get_incidents(item['source']['incident-id'])
                    self.AS_obj.post_data(json.dumps(response.json()), self.log_type)
                    
                    #handling time
                    self.get_new_time(response)

                if(item['source']['alert-id'] is not None):
                    response = self.DS_obj.get_alerts(item['source']['alert-id'])
                    self.AS_obj.post_data(json.dumps(response.json()), self.log_type)
                    #handling time
                    self.get_new_time(response)

        
        self.date.update_new_time()