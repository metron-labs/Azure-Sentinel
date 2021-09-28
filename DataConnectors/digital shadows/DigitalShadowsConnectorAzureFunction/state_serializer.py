""" handle and save last updated time here """
from datetime import datetime
from datetime import timedelta
import logging
from azure.storage.fileshare import ShareClient
from azure.storage.fileshare import ShareFileClient
from azure.core.exceptions import ResourceNotFoundError

class State:
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

    """ gets the last updated time"""
    def generate_date(self):
        #self.after_time = datetime.strptime("2021-09-01 05:23:25", "%Y-%m-%d %H:%M:%S")
        current_time = datetime.utcnow() - timedelta(minutes=15)
        past_time = self.get()
        if past_time is not None:
            logging.info("The last time point is: {}".format(past_time))
        else:
            logging.info("There is no last time point, trying to get events from last 20 days.")
            past_time = (current_time - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        self.post(current_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
        return (past_time, current_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"))


