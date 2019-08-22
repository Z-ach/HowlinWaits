import csv
from datetime import datetime, timedelta
from collections import OrderedDict
from operator import itemgetter

day_dict = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

class Data():
    def data_sort(self, num_days=None):
        times = OrderedDict()
        date_limit = datetime.now()
        if num_days: date_limit -= timedelta(days=num_days)
        else: date_limit -= timedelta(days=9000)

        with open("tweets.csv", "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            for id, date, wait_time in csv_reader:
                datetime_date = datetime.strptime(date, "%Y-%m-%d %X")
                #print("{}, {}".format(datetime_date.strftime("%a, %x, %I:00 %p"), wait_time))
                if datetime_date < date_limit: break
                #print(datetime_date.strftime("%a %x %I:00%p"), wait_time)
                if datetime_date.weekday() not in times:
                    times[datetime_date.weekday()] = OrderedDict()
                if datetime_date.hour not in times[datetime_date.weekday()]:
                    times[datetime_date.weekday()][datetime_date.hour] = list()
                tmp_list = times[datetime_date.weekday()][datetime_date.hour]
                tmp_list.append(wait_time)
                times[datetime_date.weekday()][datetime_date.hour] = tmp_list
        return times

    def average_data(self, data):
        averages = OrderedDict()
        wait_times_processed = 0
        for day, hours in data.items():
            for hr, entries in hours.items():
                sum = 0
                if len(entries) < 2: continue
                wait_times_processed += len(entries)
                for entry in entries:
                    sum += float(entry)
                averages["{} - {}:00".format(day_dict[day], str(hr))] = sum/len(entries)
        print("Processed {} wait times.".format(wait_times_processed))
        return averages

    def print_data(self, data):
        print("----ALL TIMES----")
        all_times = list()
        day_list = [day_dict[day] for day in range(7)]
        for day in day_list:
            times = list()
            for day_time, wait in data.items():
                if day in day_time:
                    tup = (day, day_time[-5:], wait)
                    times.append(tup)
            times.sort(key=itemgetter(1))
            all_times.extend(times)
        for day, hour, wait in all_times:
            print("{} {} - {}".format(day, hour, "{:.2f}".format(wait)))

        print("----5 BEST TIMES----")
        limit = 5
        for day_time, wait_time in sorted(data.items(), key=itemgetter(1)):
            print("{} {}".format(day_time, "{0:.2f}".format(wait_time)))
            limit -= 1
            if limit == 0: break
