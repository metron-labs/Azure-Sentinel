""" polls data from DS to azure logs """
from . import DS_api
from . import AS_api
from . import state_serializer
import json

class poller:
    log_type = 'InALogs'                    #custom logs name

    def __init__(self, ds_id, ds_key, secret, as_id, as_key, connection_string):
        self.DS_obj = DS_api.api(ds_id, ds_key, secret)
        self.AS_obj = AS_api.logs_api(as_id, as_key)
        self.date = state_serializer.state()
        self.date.generate_date(connection_string)

    def poll(self):
        event_data = json.loads(self.DS_obj.get_triage_events(self.date.after_time, self.date.before_time))
        
        for event in event_data:            
            item_data = json.loads(self.DS_obj.get_triage_items(event['triage-item-id']))
            
            #sending data to sentinel
            for item in item_data:
                if(item['source']['incident-id'] is not None):
                    response = self.DS_obj.get_incidents(item['source']['incident-id'])
                    self.AS_obj.post_data(json.dumps(response.json()), self.log_type)

                if(item['source']['alert-id'] is not None):
                    response = self.DS_obj.get_alerts(item['source']['alert-id'])
                    self.AS_obj.post_data(json.dumps(response.json()), self.log_type)
