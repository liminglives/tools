import csv
import datetime
import pandas
datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

filename = "rtt.large.csv3"

import time
start = time.time();


f = file(filename, "rb")
df = csv.reader(f)


#df = pandas.read_csv(filename)

end = time.time()
print end - start

#print df["MarketCov"][0:10]
