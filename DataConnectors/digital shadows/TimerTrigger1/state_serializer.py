#handle and save last updated time here
from datetime import datetime
import pickle

class state:
    before_time = datetime.now()

    #converts datetime string to DS type time
    def convert_to_DS_time(date, hour, minute, second):
        parsed_str = date + "T" + hour + "%3A" + minute + "%3A" + second + ".000Z"  
        return parsed_str

    def convert_to_datetime(date_var):
        date = str(date_var[0:10]).split('-')
        time = str(date_var[11:19]).split(':')
        parsed_date = datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]))
        return parsed_date


    #gets the last updated time from the pickle file
    def get_last_updated(self):     
        try:
            f = open('timestore.pckl', 'rb')
            self.after_time = pickle.load(f)
            f.close()
        except (EOFError, FileNotFoundError) as e:
            self.after_time = datetime.strptime("2021-09-01 05:23:25", "%Y-%m-%d %H:%M:%S")


    #updates new time in the pickle file
    def update_new_time(self):
        temp_date = datetime(1800, 10, 10)

        f = open('timestore.pckl', 'wb')
        pickle.dump(temp_date, f)
        f.close()
        f = open('timestore.pckl', 'wb')
        pickle.dump(self.after_time, f)
        f.close()


    