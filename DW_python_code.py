import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import string
import codecs
import json
import pymongo
from pymongo import MongoClient

filename='/users/ambilurama/Downloads/Nano/data_wrangling/southampton_england.osm'


street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)

def count_tags(files):
    '''This function counts the number of unique tags in the given file '''
    osm_file = open(files, "r")
    dicti={}
    for event, elem in ET.iterparse(osm_file, events=("start", "end")):
        if event == 'start':
            taag=elem.tag
            if taag in dicti:
                count=dicti[taag]+1
                dicti[taag]= count
            else:
                dicti[taag]=1
    osm_file.close()
    return dicti
tag_count=count_tags(filename)
pprint.pprint(tag_count)

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    ''' This function identifies and counts the Problematic tags '''
    
    if element.tag == "tag":
        
        value= element.get('k')
            
        if re.search(lower,value):
            keys['lower'] += 1
        elif re.search(lower_colon,value):
            keys['lower_colon'] += 1
        elif re.search(problemchars,value):
            keys['problemchars'] += 1
        else:
            keys['other'] += 1   
            
       
        pass
        
    return keys



def key_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

key = key_map(filename)
pprint.pprint(key)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]
#add st:street,ctr:center,hwy:highway

mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "Dr" :"Drive",
            "CT" :"Court",
            "Ct" :"Court",
            "Rd" :"Road",
            "Rd." :"Road",
            "Sq": "Square",
            "PKWY":"Parkway",
            "N." :"North",
           "S." :"South",
           "blvd.":"Boulevard",
           "Blvd":"Boulevard",
           "soc.":"Soceity"
            }

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)




def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(filename):
    osm_file = open(filename, "r")

    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):


        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()

    return street_types

def update_name(name, mapping):
    '''This function updates all the abbreviated street names with the given mapping names'''
    key = mapping.keys()
    
    bn =""
    for n in name.split(" "):
        
        if n in key:
            
            nn = mapping[n]
            if bn=="":
                bn +=nn
            else:
                bn = bn +" " +nn
        else:
            if bn=="":
                bn +=n
            else:
                bn = bn +" " +n
         
    return bn

def test():
    
    st_types = audit(filename)
    pprint.pprint(dict(st_types))


    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            
test()                        


CREATED = [ "version", "changeset", "timestamp", "user", "uid"]




lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

postalcode = ["SO14","SO15","SO16","SO17","SO18","SO19","SO20","SO21","SO22","SO23","SO24","SO30","SO31","SO32","SO40",
              "SO41","SO42","SO43","SO44","SO45","SO50","SO51","SO52","SO53"]
def update_postcode(postc):
    '''This function update the problematic postal codes to the expected format.problematic postal codes have lowercase ,lacking of space right after outward postcode.'''
    
    value= postc.lower()
    match = re.search(r'so\d\d\s\d\w\w', value)
    if match:
        return value.upper()
    elif len(value)<8:
        tune= value[:4] +' ' + value[4:]
        return tune.upper()
    else:
        return "error"

print update_postcode("So40 4wr")
print update_postcode("so16 8hy")
print update_postcode("SO172FZ")
print update_postcode("SO16 8HY")

def shape_element(element):
    ''' This function performs data modeling on given data resulting the data in an expected format'''
    node = {}
    addr={}
    node_ref=[]
    postcheck = set()
    if element.tag == "node":
        node["created"] ={}
        node["pos"] =[]
        
        node["id"]=element.get("id")
        node["type"]=element.tag
        node["visible"]=element.get("visible")
        for i in range(len(CREATED)):
            
            label = element.get(CREATED[i])
            node["created"][CREATED[i]]=label
            lat=float(element.get('lat'))
            lon=float(element.get('lon'))
        node["pos"].append(lat)
        node["pos"].append(lon)
    
    
    if element.tag == "node" or element.tag == "way" :
        for child in element:
            
            if child.tag == 'tag':
                
                valuek=child.get("k")
                
                tt=["amenity","cuisine","name","phone"]
                if valuek in tt:
                    node[valuek]=child.get("v")
                
                if valuek.count(":")==1:
                    tu =valuek.find(":")
                    checkk=valuek[tu+1:]
                    
                    vv=["housenumber","postcode","street"]
                    
                    if checkk in vv:
                        if checkk=="postcode":
                            updated= update_postcode(child.get("v"))
                            if updated=="Error ":
                                print child.get("v")
                            else:
                                addr[checkk]=updated
                        
                        else:
                            addr[checkk]=child.get("v")
                    
                    
                    node["address"]=addr
        
        
        
        if element.tag=="way":
            for child in element:
                
                if child.tag == 'nd':
                    valuer=child.get("ref")
                    node_ref.append(valuer)
            node["node_refs"]=node_ref
        
        
        return node
    else:
        return None
def process_map(file_in, pretty = False):
    '''this function writes the json data into a json file'''
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

data = process_map(filename, False)

print "length of the data file" ,len(data)

import os


def convert_bytes(filename):
    """
        this function will convert bytes to MB.... GB... etc
        """
    num = os.path.getsize(filename)
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

southampton_osm = '/users/ambilurama/Downloads/Nano/data_wrangling/southampton_england.osm'
temp_osm=convert_bytes(southampton_osm)
southampton_json = '/users/ambilurama/Downloads/Nano/data_wrangling/southampton_england.osm.json'
temp_json=convert_bytes(southampton_json)

print "File size\n"
print "Southampton.osm       ", temp_osm
print "Southampton.osm.json  ",temp_json

''' Creating a database named 'maps and a collection called S_E_city'''

print " Creating a database named 'maps'"
client = MongoClient('localhost:27017')
db = client.maps

print db.S_E_city

def insert_data(data):
    '''this function inserts the json data into the database named "maps"'''
    for d in data:
        db.S_E_city.insert_one(d)
    return db

print " Inserting the json data into the database "
insert_data(data)

print "finding the number of items in the DB"
print db.S_E_city.find().count()

''' print out the first element of the DB'''
print db.S_E_city.find_one()

print "The number of posts created by 'monxton' is"


print db.S_E_city.find({"created.user":"monxton"}).count()

print " The number of posts created by the user with id '534393' is "
print db.S_E_city.find({"created.uid":"534393"}).count()

print "The number of posts with 'type = node' is"
print db.S_E_city.find({'type' :'node'}).count()

print "The number of posts with 'type = way' is"
print db.S_E_city.find({'type' :'way'}).count()

print "The number of posts with type which is not node is"
print db.S_E_city.find({'type' :{"$ne":'node'}}).count()


def printtheresult(data):
    '''This function print outs the data sent into this function'''
    for d in data:
        print d



print "\nThe top 20 users who created most posts are "
query = [{"$group":{"_id":"$created.user", "count":{"$sum":1}}},{"$sort":{"count":-1}},{"$limit":20}]
results = db.S_E_city.aggregate(query)
printtheresult(results)



print "\nThe top 10 postcodes based on the counts  are"
query = [{"$match":{"address.postcode":{"$exists":1}}},
         {"$group":{"_id":"$address.postcode", "count":{"$sum":1}}},{"$sort":{"count":-1}},{"$limit" : 10}]
results = db.S_E_city.aggregate(query)
printtheresult(results)


print "\nThe data which has the postcode 'SO17 1QG' are"

query = [{"$match":{"address.postcode":"SO17 1QG"}},
         
         {"$sort":{"count":-1}}]
results = db.S_E_city.aggregate(query)
printtheresult(results)

print "\nThe most used outward postcode is "


query = [{"$match":{"address.postcode":{"$exists":1}}},
         {"$project":{"address.street":1,
         "outward postcode": { "$substr": [ "$address.postcode", 0, 4 ] }}},
         {"$group":{"_id":{"postcode":"$outward postcode"},
         "count":{"$sum" :1}}},
         
         {"$sort":{"count":-1}},
         {"$limit":10}]
results=db.S_E_city.aggregate(query)
printtheresult(results)

print "\nThe unique street names in the given outward postcode are"

query = [{"$project":{"address.street":1,
         "outward postcode": { "$substr": [ "$address.postcode", 0, 4 ] }}},
         {"$match":{"outward postcode":{"$eq":"SO17"}}},
         
         {"$group":{"_id":{"postcode":"$outward postcode"},
         "unique_street":{"$addToSet" :"$address.street"},
         "street_count":{"$sum" :1}}}
         
         ]
results=db.S_E_city.aggregate(query)
printtheresult(results)

print "\nThe number of unique streets in the given outwardpostcode is"

query = [{"$project":{"address.street":1,
         "outward postcode": { "$substr": [ "$address.postcode", 0, 4 ] }}},
         {"$match":{"outward postcode":{"$eq":"SO17"}}},
         
         {"$group":{"_id":{"postcode":"$outward postcode"},
         "unique_street":{"$addToSet" :"$address.street"}
         }},
         { "$unwind": "$unique_street" },
         {"$group": {"_id":{"postcode":"SO17"},"unique_street_count": { "$sum": 1 }}}
         ]

results=db.S_E_city.aggregate(query)

printtheresult(results)

print "\nThe top5 contributors based on their contribution ratio are"

total_count = db.S_E_city.find({'type' :'node'}).count()
query = [{"$group":{"_id":"$created.user", "count":{"$sum":1}}},
         {"$project":{"Contribution ratio":
         {"$multiply":[{"$divide":["$count",total_count]},100] }}},
         
         {"$sort":{"Contribution ratio": -1}},{"$limit":5}]
results = db.S_E_city.aggregate(query)
printtheresult(results)


print "\n certain datas are"

print data[-1]
print data[-2000]
print data[-5]
print data[0]