import datetime
import logging
#import pickle
from . import DS_poller
import azure.functions as func
import os

account_id = os.environ['ACCOUNT_ID']
passkey = bytes(os.environ['PASSKEY'], 'utf-8')
customer_id = os.environ['CUSTOMER_ID']
shared_key = os.environ['SHARED_KEY']
key = os.environ['KEY']
secret = os.environ['SECRET']
''' 
from . import from_DS

#try to open a pickle file and if it is empty then exception
try:
  f = open('timestore.pckl', 'rb')
  max_time = pickle.load(f)
  f.close()
except (EOFError, FileNotFoundError) as e:
  max_time = datetime.datetime.strptime("2021-09-01 05:23:25", "%Y-%m-%d %H:%M:%S")       #datetime() 

 '''

max_time = datetime.datetime.strptime("2021-09-01 05:23:25", "%Y-%m-%d %H:%M:%S")

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    
    DSobj = DS_poller.poller(account_id, key, secret, customer_id, shared_key)

    DSobj.poll()