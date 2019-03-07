import bitly_api

API_KEY = 'R_b3f62ac5f5e649c29e80daf56d789849'
API_USER = 'o_2p818mf0hq'
b = bitly_api.Connection(API_USER, API_KEY)


BASE_URL = 'http://www.kiwi.com/deep?affilid=193land&'
ADDITIONAL_INFO = '&airportsList=LTN%2CLGW%2CSTN&selectedStopoverAirportsExclude=true&stopNumber=0&lang=en&currency=eur&passengers=1'

from_city = "from=" + raw_input('Please, input city/country or IATA code(s) for departure destination: ')
to_city = "to=" + raw_input('Please, input city/country or IATA code(s) for arrival destination: ')
from_date = "departure=" + raw_input('Please, input departure date or date range: ').replace(' ', '_')
to_date = "return=" + raw_input('Please, input return date or date range or time to stay: ').replace(' ', '_')
max_duration_time = raw_input('OPTIONAL. Enter max stop time: ')
max_duration_time = "stopDurationMax=" + max_duration_time if max_duration_time else "stopDurationMax=25"

parameters = '&'.join([from_city, to_city, from_date, to_date, max_duration_time])

print("Your url is: {}".format(b.shorten(BASE_URL+parameters+ADDITIONAL_INFO)['url']))
