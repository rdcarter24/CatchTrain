from urllib2 import urlopen
from lxml import etree
import math
import time
import datetime

# takes a users location and destination BART and sends a text message when it's time to leave.

user_location =[37.7884615, -122.4151477]
destination = "NBRK"
mode = "DRIVING"

def get_closest_BART(user_location):
    # Use users geolocation to find closest BART

    # Below code was used to consruct BART_stations_locations dictionary
    # location_dict = {}
    # key = "&key=MW9S-E7SL-26DU-VV8V"
    # url = "http://api.bart.gov/api/stn.aspx?cmd=stns"
    # url += key
    # response = urlopen(url)
    # doc = etree.parse(response)
    # response.close()
    # root = doc.getroot()
    # names = root.findall('stations/station/abbr')
    # latitudes = root.findall('stations/station/gtfs_latitude')
    # longitudes = root.findall('stations/station/gtfs_longitude')
    # for i in range(len(names)):
    #     location_dict[names[i].text]=[latitudes[i].text,longitudes[i].text]


    BART_stations_locations = {'SHAY': ['37.63479954', '-122.0575506'], 'FTVL': ['37.774963', '-122.224274'],
    'CIVC': ['37.779528', '-122.413756'], 'COLS': ['37.754006', '-122.197273'], 'PLZA': ['37.9030588', '-122.2992715'],
    'WOAK': ['37.80467476', '-122.2945822'], 'CONC': ['37.973737', '-122.029095'], 'NCON': ['38.003275', '-122.024597'],
    'SFIA': ['37.616035', '-122.392612'], 'WDUB': ['37.699759', '-121.928099'], 'DALY': ['37.70612055', '-122.4690807'],
    '24TH': ['37.752254', '-122.418466'], 'SBRN': ['37.637753', '-122.416038'], 'HAYW': ['37.670399', '-122.087967'],
    'LAFY': ['37.893394', '-122.123801'], 'DBRK': ['37.869867', '-122.268045'], '12TH': ['37.803664', '-122.271604'],
    'PHIL': ['37.928403', '-122.056013'], 'PITT': ['38.018914', '-121.945154'], 'CAST': ['37.690754', '-122.075567'],
    'MONT': ['37.789256', '-122.401407'], 'POWL': ['37.784991', '-122.406857'], 'ROCK': ['37.844601', '-122.251793'],
    'SANL': ['37.72261921', '-122.1613112'], '16TH': ['37.765062', '-122.419694'], 'SSAN': ['37.664174', '-122.444116'],
    'BALB': ['37.72198087', '-122.4474142'], 'DELN': ['37.925655', '-122.317269'], 'MCAR': ['37.828415', '-122.267227'],
    'DUBL': ['37.701695', '-121.900367'], 'EMBR': ['37.792976', '-122.396742'], 'WCRK': ['37.905628', '-122.067423'],
    'MLBR': ['37.599787', '-122.38666'], 'GLEN': ['37.732921', '-122.434092'], 'NBRK': ['37.87404', '-122.283451'],
    'ORIN': ['37.87836087', '-122.1837911'], 'BAYF': ['37.697185', '-122.126871'], 'LAKE': ['37.797484', '-122.265609'],
    'ASHB': ['37.853024', '-122.26978'], 'UCTY': ['37.591208', '-122.017867'], '19TH': ['37.80787', '-122.269029'],
    'COLM': ['37.684638', '-122.466233'], 'RICH': ['37.936887', '-122.353165'], 'FRMT': ['37.557355', '-121.9764']}

    # build a dictionary with key = station and value = distance between station and user, find min value
    diff_dict = {}
    for key in BART_stations_locations:
        diff_dict[key] = math.sqrt((float(user_location[0])-float(BART_stations_locations[key][0])
            )**2+(abs(float(user_location[1]))-abs(float(BART_stations_locations[key][1])
            ))**2)

    closest_BART = min(diff_dict,key=diff_dict.get)

    # closest_BART_info = [station abrev, latitude, longitude] all strings
    closest_BART_info = [closest_BART, BART_stations_locations[closest_BART][0], BART_stations_locations[closest_BART][1]]
    return closest_BART_info


def get_time_to_BART(user_location, closest_BART, mode):
    # get time to nearest BART, mode = walking/driving/bicycing

    url = "https://maps.googleapis.com/maps/api/distancematrix/xml?"
    url += "origins="
    url += str(user_location[0])
    url += ","
    url += str(user_location[1])
    url += "&destinations="
    url += closest_BART[1]
    url += ","
    url += closest_BART[2]
    url += "&sensor=true"
    url += "&mode="
    url += mode

    response = urlopen(url)
    doc = etree.parse(response)
    response.close()

    root = doc.getroot()
    time_to_BART = root.find('row/element/duration/text')

    return time_to_BART.text.strip(" mins")


def get_departure_time(origin, destination, time_to_BART):
    # Get departure times from bart API

    url = "http://api.bart.gov/api/sched.aspx?cmd=depart"
    url += "&orig="
    url += origin[0]
    url += "&dest="
    url += destination
    url += "&date=now"
    url += "&key=MW9S-E7SL-26DU-VV8V"
    url += "&b=2&a=2&l=1"


    response = urlopen(url)
    doc = etree.parse(response)
    response.close()

    root = doc.getroot()

    # get current time, can also use datetime
    time = root.find('schedule/time').text
    time = datetime.datetime.strptime(time,'%H:%M %p')

    # arrive_to_BART_time = current time + time it takes to get to BART
    arrive_to_BART_time = time + datetime.timedelta(minutes=int(time_to_BART))

    # for all departure times, if the time you arrive to BART is before the departure time,
    # send text when it's time to leave, else try next time
    elements = root.findall('schedule/request/trip')
    for element in elements:
        element.get("origTimeMin")
        depart_from_BART_time = datetime.datetime.strptime(element.get("origTimeMin"),'%H:%M %p')
        if  arrive_to_BART_time.time() <= depart_from_BART_time.time():
            return "Send text"
        else:
            pass




get_departure_time(get_closest_BART(user_location), destination, get_time_to_BART(user_location, get_closest_BART(user_location), mode))





