#!./venv/bin/python

# from flask import request #, make_response

from flask import request, render_template, make_response
from twilio.rest import TwilioRestClient
from time import time
import httplib  
import urllib
import json

from math import *

from app import app
from . import valueFromRequest
import sqlite3 as lite

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return 'You want path: %s' % path

@app.route('/')
def index():
	''' This is the basic app page '''
		
	templateDict = {}#{"header":"Is it cape weather?"}
	return render_template("index.html", **templateDict)

""""
@app.route('/getWeather', methods=['GET', 'POST'])
def getWeather():
	'''
	If accepting both GET and POST methods, use the local
	"valueFromRequest" method (defined in controllers.__init__.py).
	This handles both methods, and you can specify whether each
	parameter value should be made lower case, returned as a Boolean
	(e.g. for flags with no value), or parsed into a list from a
	comma-separated string.
	'''
	lat = float(valueFromRequest(key="lat", request=request))
	long = float(valueFromRequest(key="long", request=request))

	results=getWeatherFromAPI(lat,long)
		
	response=make_response(json.dumps(results))
	response.headers["Access-Control-Allow-Origin"]="http://isitcapeweather.com"
	return response
"""

@app.route('/sendASPStatusAsText', methods=['GET'])
def sendASPStatusAsText():
	number = valueFromRequest(key="number", request=request)
	return str(number)
	currentASP=""
	currentASP = json.load(open("/home/jproberts00/isASPActive.jrsandbox.com/public/static/parking.json"))
	currentASP = currentASP.split('\n')[0].replace("<p>","").replace("</p>","")

	# put your own credentials here 
	ACCOUNT_SID = "ACf274d99e39b7edc9a7e2966be84845ac" 
	AUTH_TOKEN = "ab49a1be379fd077971ba5fc2c312f35" 
	 
	client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 
	 
	result = client.messages.create( 
		to=number, 
		from_="+13475779530", 
		body=currentASP,
	)
	templateDict = {"data":"test","number":number,"ASP":currentASP,"result":result}#{"header":"Is it cape weather?"}
	return render_template("result.html", **templateDict)

@app.route('/getRoads', methods=['GET'])
def getRoads():
	theLat = valueFromRequest(key="lat", request=request)
	theLong = valueFromRequest(key="long", request=request)

	#return str(theLat)+","+str(theLong)
	results=ReadFromDBToJSON(theLong,theLat)
	#return str(results)	

	response=make_response(json.dumps(results))
	response.headers["Access-Control-Allow-Origin"]="http://311asp.com"
	return response

@app.route('/getStatus', methods=['GET'])
def get_status_text():
	results = json.load(open('/home/jproberts00/311asp.com/public/static/parking.json'))

	response=make_response(json.dumps({"status":results.strip().replace("<p>","").replace("</p>","")}))
	response.headers["Access-Control-Allow-Origin"]="http://311asp.com"
	return response

PARKINGSIGNS_SQL='app/parking.db'
MAXIMUM_SIGN_DISTANCE = 0.002
con = lite.connect(PARKINGSIGNS_SQL)




def ParseStreetCleaningTimes(signDescParsed):
    ogString = signDescParsed

    signDescParsed = string.replace(signDescParsed,"NOON 1:3-PM","12PM-3PM")
    signDescParsed = string.split(signDescParsed,"BOL)")
    signDescParsed = string.split(signDescParsed[1],"<")
    signDescParsed = string.split(signDescParsed[0],"W/")
    signDescParsed = string.replace(signDescParsed[0].strip(),' & '," ")
    signDescParsed = string.replace(signDescParsed,' &'," ")
    signDescParsed = string.replace(signDescParsed,'& '," ")
    signDescParsed = string.replace(signDescParsed,'&'," ")
    signDescParsed = string.replace(signDescParsed,' -',"-")
    signDescParsed = string.replace(signDescParsed,'- ',"-")
    signDescParsed = string.replace(signDescParsed,'(MOON/STARS SYMBOLS)',"")
    signDescParsed = string.replace(signDescParsed,'(SINGLE ARROW)',"")
    signDescParsed = string.replace(signDescParsed,'-->',"")
    signDescParsed = signDescParsed.strip()
    signDescParsed = string.replace(signDescParsed,'MIDNIGHT',"12AM")
    signDescParsed = string.replace(signDescParsed,'NOON',"12PM")
    signDescParsed = string.replace(signDescParsed,"NO PARKING","")
    signDescParsed = string.replace(signDescParsed,'=','-')
    signDescParsed = string.replace(signDescParsed," TO ","-")
    signDescParsed = signDescParsed.strip()
    signDescParsed = string.replace(signDescParsed," TO-","-")
    signDescParsed = string.replace(signDescParsed," F RI "," FRI ")
    signDescParsed = string.replace(signDescParsed," TUE S "," TUES ")
    signDescParsed = string.replace(signDescParsed," F RI"," FRI")
    signDescParsed = string.replace(signDescParsed," PM","PM")
    signDescParsed = string.replace(signDescParsed,"8AM 11AM","8AM-11AM")
    signDescParsed = string.replace(signDescParsed,"THRUSDAY","THURSDAY")
    signDescParsed = string.replace(signDescParsed,"MON THRU FRI","MON TUES WED THUR FRI")
    signDescParsed = string.replace(signDescParsed,"MONDAY-FRIDAY","MON TUES WED THUR FRI")
    signDescParsed = string.replace(signDescParsed,"EXCEPT SUNDAY","MON TUES WED THUR FRI SAT")
    signDescParsed = string.replace(signDescParsed,"EXCEPT SUN","MON TUES WED THUR FRI SAT")

    if signDescParsed[-1:] == '-':
        signDescParsed=signDescParsed[0:-1]


    return signDescParsed

days = ['MON','TUE','WED','THU','FRI','SAT','SUN']
specialWord = ['THRU','EXCEPT']

def IsDay(s):
    isday = False
    
    for day in days:
        if day in s:
            return True


def ParseDay(s):
    for day in days:
        if day in s:
            return day

    return None

def IsSpecialWord(s):
    isspec = False
    
    for sp in specialWord:
        if sp in s:
            return True

def IsTime(s):
    if IsDay(s):
        return False
    if IsSpecialWord(s):
        return False
    
    return True

def ParseHour(s):


    if s == "12PM":
        return "12:00"
    
    if s == "12AM":
        return "00:00"
    
    ampm = s[-2:]
    
    add = 0
    if ampm == "PM" and s[:2] != "12":
        add = 12

    s = s[0:-2]
        
    minute = ":00"

    
    if ":" in s:
        minute = ":30"
        s=string.split(s,":")
        s=s[0]

    h = int(s) + add
    
    hour = str(h)
    
    if h < 10:
        hour = "0" + str(h)

    return hour + minute


    
    

def DetermineTimes(signDescParsed):
    times = []

    if signDescParsed == '':
        return times
    
    curDay = None
    curStartTime = None
    curEndTime = None

    tokens = string.split(signDescParsed)
    

    if IsDay(tokens[0]):
        newTokens = []
        newTokens.append(tokens[len(tokens)-1])
        for i in range(len(tokens)-1):
            newTokens.append(tokens[i])
        tokens=newTokens


    for i in range(len(tokens)):
        toke = tokens[i]
        if IsTime(toke):
            curTimes = string.split(toke,'-')
            if curTimes[0][-2:] != 'AM' and curTimes[0][-2:] != 'PM':
                curTimes[0] = curTimes[0] + curTimes[1][-2:]
            if curTimes[1][-2:] != 'AM' and curTimes[1][-2:] != 'PM':
                curTimes[1] = curTimes[1] + curTimes[0][-2:]

            curStartTime = ParseHour(curTimes[0])
            curEndTime = ParseHour(curTimes[1])

            if curDay != None:
                entry = {}
                entry['day']=curDay
                entry['start']=curStartTime
                entry['end']=curEndTime
                times.append(entry)

                curStartTime = None
                curEndTime = None

        elif IsDay(toke):
            curDay = ParseDay(toke)
                
            if curDay == None:
                continue

            if curStartTime!=None:
                entry = {}
                entry['day']=curDay
                entry['start']=curStartTime
                entry['end']=curEndTime
                times.append(entry)
                curDay=None


    return times




# non url apps
def ReadFromDBToJSON(lon, lat):
    maxDist = MAXIMUM_SIGN_DISTANCE
    
    minLon = float(lon) - maxDist
    maxLon = float(lon) + maxDist
    minLat = float(lat) - maxDist
    maxLat = float(lat) + maxDist
    
    retJson = []

    with con:
    
        cur = con.cursor()
        selectStr = "SELECT * from ParkingSigns WHERE LON > " + str(minLon) + " AND LON < " + str(maxLon) + " AND LAT > " + str(minLat) + " AND LAT < " + str(maxLat) + " AND STREETCLEANING=1"
        cur.execute(selectStr)
        signs = cur.fetchall()
        
        for sign in signs:
            curEntry = {}
            curEntry["INDEX"] = sign[0]
            curEntry["SG_ORDER_N"] = sign[1]
            curEntry["LON"] = sign[2]
            curEntry["LAT"] = sign[3]
            curEntry["STREET"] = sign[4]
            curEntry["CROSSSTREET1"] = sign[5]
            curEntry["CROSSSTREET2"] = sign[6]
            curEntry["SIDE"] = sign[7]
            curEntry["STREETCLEANING"] = sign[8]

            curEntry["STREETCLEANINGTIMES"] = []

            signDescParsed = sign[9]

            if sign[8] == 1:
                signDescParsed=ParseStreetCleaningTimes(signDescParsed)
                curEntry["STREETCLEANINGTIMES"]=DetermineTimes(signDescParsed)
                
            curEntry["SIGNDESC1"] = signDescParsed

            retJson.append(curEntry)

	    
    retJson_top = get_top_results(retJson, lon, lat, N=30)
            
    return retJson_top


def get_distance(lon1, lat1, lon2, lat2):
    """
    Given lon,lat for two positions (assumed to be nearby), return the physical distance 
    of the 2 points in meters.
    """
    R_earth = 6.371e6 # in meters
    pi=3.14159265359
    l1= float(lon1)*pi/180.
    b1= float(lat1)*pi/180.
    l2=float(lon2)*pi/180.
    b2=float(lat2)*pi/180.
    # get angular distance in radians
    angular_dist = 2*asin(sqrt((sin((b1-b2)/2))**2 + cos(b1)*cos(b2)*(sin((l1-l2)/2))**2))
    return R_earth*angular_dist # physical distance

def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key = seq.__getitem__)
    
def get_top_results(subset, lon, lat, N=5):
    """
    Takes 'subset' (a list of parking entries from database query); lon,lat of point of interest
    and the number of entries to return, sorted by distance in meters. The 'DIST' key has also 
    been added to each dictionary in the returned list.
    """
    d   = [get_distance(lon, lat, item['LON'], item['LAT']) for item in subset]
    top = []
    for i in range(min(N, len(d))): # return at most N entries
        enriched_dict = subset[argsort(d)[i]]
        enriched_dict.update({ 'DIST': d[argsort(d)[i]] }) # add distance to dict
        top.append(enriched_dict)
    return top

