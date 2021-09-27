""" handle and save last updated time here """
from datetime import datetime
from datetime import timedelta
import logging
from azure.storage.fileshare import ShareClient
from azure.storage.fileshare import ShareFileClient
from azure.core.exceptions import ResourceNotFoundError

class StateManager:
    def __init__(self, connection_string, share_name='funcstatemarkershare', file_path='funcstatemarkerfile'):
        self.share_cli = ShareClient.from_connection_string(conn_str=connection_string, share_name=share_name)
        self.file_cli = ShareFileClient.from_connection_string(conn_str=connection_string, share_name=share_name, file_path=file_path)

    def post(self, marker_text: str):
        try:
            self.file_cli.upload_file(marker_text)
        except ResourceNotFoundError:
            self.share_cli.create_share()
            self.file_cli.upload_file(marker_text)

    def get(self):
        try:
            return self.file_cli.download_file().readall().decode()
        except ResourceNotFoundError:
            return None

class state:

    """ converts datetime string to DS type time """
    def convert_to_DS_time(date, hour, minute, second):
        parsed_str = date + "T" + hour + "%3A" + minute + "%3A" + second + ".000Z"  
        return parsed_str

    """ gets the last updated time"""
    def generate_date(self, connection_string):
        #self.after_time = datetime.strptime("2021-09-01 05:23:25", "%Y-%m-%d %H:%M:%S")
        current_time = datetime.utcnow() - timedelta(minutes=15)
        state_now = StateManager(connection_string)
        past_time = state_now.get()
        if past_time is not None:
            logging.info("The last time point is: {}".format(past_time))
        else:
            logging.info("There is no last time point, trying to get events from last 10 days.")
            past_time = (current_time - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        state_now.post(current_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
        (self.after_time, self.before_time) = (past_time, current_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
        logging.info("After time: %s", self.after_time)
        logging.info(" to before time: %s", self.before_time)

    def convert_to_datetime(date_var):
        date = str(date_var[0:10]).split('-')
        time = str(date_var[11:19]).split(':')
        parsed_date = datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]))
        return parsed_date


    

