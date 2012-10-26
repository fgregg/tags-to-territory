import flickrapi
from xml.dom.minidom import parseString
from xml.etree import ElementTree
import MySQLdb
import re
from geopy import geocoders
from geopy.geocoders.google import GQueryError
import time
import secrets

def prettyPrint(element):
    txt = ElementTree.tostring(element)
    print parseString(txt).toprettyxml() 

def photoList(photos) :
    photo_list = []
    for photo in photos :
        photo_list.append({'id': photo.attrib['id'],
                           'latitude': photo.attrib['latitude'] ,
                           'longitude' : photo.attrib['longitude'] ,
                           'title': photo.attrib['title'] ,
                           'owner': photo.attrib['ownername'] ,
                           'description': photo.find('description').text,
                           'date_taken' : photo.attrib['datetaken'],
                           'date_upload' : photo.attrib['dateupload'],
                           'tags' : photo.attrib['tags']
                           }
                          )
    return(photo_list)
                         

def photoWriteDatabase(photo_list) :
    db = MySQLdb.connect(db="chicago_gangs",
                         read_default_file="~/.my.cnf",
                         charset="utf8",
                         use_unicode=True)
    c = db.cursor()

    for photo in photo_list :
        print int(photo['id'])
        c.execute("""
        INSERT IGNORE INTO tag
        (image_id, title, description, lat_long, owner, date_taken, date_upload, tags)
        VALUES
        (%s, %s, %s, PointFromText('POINT(%s %s)'), %s, %s, %s, %s)""",
                  (int(photo['id']),
                   photo['title'],
                   photo['description'],
                   float(photo['longitude']),
                   float(photo['latitude']),
                   photo['owner'],
                   photo['date_taken'],
                   photo['date_upload'],
                   photo['tags']
                   )
                  )

    c.close()

gang_grafitti_nsid = '432182@N25'
chicago_gang_grafitti_nsid = '1305490@N25'

fields = "description,date_taken, owner_name, geo, tags, date_taken, date_upload" 

api_key = secrets.api_key
print 'Authenticating with Flickr:',
flickr = flickrapi.FlickrAPI(api_key, format='etree')
print 'Done'

print 'Getting Flickr Data:'
gg_sets = photoList(flickr.walk(group_id = chicago_gang_grafitti_nsid,
                                 extras = fields))
print ' Done'
## gg_sets += photoList(flickr.walk(group_id = gang_grafitti_nsid,
##                                  has_geo = 1,
##                                  extras = fields))
## gg_sets += photoList(flickr.walk(text = "gang tag",
##                                  bbox = "-90,40,-86,44",
##                                  has_geo = 1,
##                                  extras = fields))
## gg_sets += photoList(flickr.walk(text = "gang grafitti",
##                                  bbox = "-90,40,-86,44",
##                                  has_geo = 1,
##                                  extras = fields))
## gg_sets += photoList(flickr.walk(text = "gang graffiti",
##                                  bbox = "-90,40,-86,44",
##                                  has_geo = 1,
##                                  extras = fields))
## gg_sets += photoList(flickr.walk(text = "chicagoganggraffiti",
##                                  bbox = "-90,40,-86,44",
##                                  has_geo = 1,
##                                  extras = fields))
## gg_sets += photoList(flickr.walk(text = "chicagogangtags",
##                                  bbox = "-90,40,-86,44",
##                                  has_geo = 1,
##                                  extras = fields))
## gg_sets += photoList(flickr.walk(text = "ganggraffiti",
##                                  bbox = "-90,40,-86,44",
##                                  has_geo = 1,
##                                  extras = fields))
## ggf_sets += photoList(flickr.walk(text = "gangtags",
##                                   bbox = "-90,40,-86,44",
##                                   has_geo = 1,
##                                   extras = fields))

photoWriteDatabase(gg_sets)


db = MySQLdb.connect(db="chicago_gangs",
                     read_default_file="~/.my.cnf",
                     charset="utf8",
                     use_unicode=True)
c = db.cursor()

c.execute("select image_id from tag where sets is null")

image_ids = c.fetchall()
for image_id in image_ids :
    try:
        photo_contexts = flickr.photos_getAllContexts(photo_id = image_id[0])
        image_set = photo_contexts.find('set').attrib['title']
    except :
        image_set = "none"
    c.execute("update tag set sets = %s where image_id = %s",
              (image_set, image_id[0])
              )
    try:
        print(unicode(image_set))
    except:
        print "oh well"
     
    
c.close()

db = MySQLdb.connect(db="chicago_gangs",
                     read_default_file="~/.my.cnf",
                     charset="utf8",
                     use_unicode=True)
c = db.cursor()

c.execute("select image_id, description from tag where tags is not null and X(lat_long) = 0")


descriptions = c.fetchall()

geo = geocoders.Google()    

counter = 0
for description in descriptions :
    image_id, description = description
    if description :
        description = description.replace('\n', ' ')
        description = description.replace("&amp;", "&")
        description = description.replace('&quot;', '"')
        description = description.replace('Mc +Lean;', 'McLean')
        description = re.sub(".*?([Cc]lose to|on|On|ON|Near|near|by|vicinity of|at|of) [a-z ]*([A-Z0-9]\\w+?\\b) *[A-Za-z.]*( vicinity | and | towards | near | n | *& *| */ *| [Ww]est | [Ee]ast | [Ss]outh | [Nn]orth )[a-z ]*([A-Z0-9]\\w+\\b) *([A-Z]\\w)*.*", "\\2 & \\4, Chicago, IL", description)
        description = re.sub(".*([A-Z0-9]\\w+\\b) *([A-Z]\\w)*( near | and | *& *| */ *)[a-z ]*([A-Z0-9]\\w+?\\b) *[A-Za-z]*[\W]*(Gang [Gg]raffiti)*.$", "\\1 & \\4, Chicago, IL", description)
        description = re.sub(".*(vicinity of|[Bb]etween) ([A-Z0-9]\\w+\\b) *[A-Za-z.]*( and | *& *| */ *| to )[a-z ]*([A-Z0-9]\\w+\\b)[,a-z ]*([A-Z]\\w+).*$", "\\4 & \\5, Chicago, IL", description)
        description = re.sub("^([A-Z0-9]\\w+?\\b) *[A-Za-z.]*( vicinity | and | near | *& *| */ *| [Ww]est | [Ee]ast | [Ss]outh | [Nn]orth )[a-z ]*([A-Z0-9]\\w+\\b).*", "\\1 & \\3, Chicago, IL", description)
#        description = re.sub("   +([A-Z0-9]\\w+\\b) *[A-Za-z.]*( vicinity | and | near | *& *| */ *| [Ww]est | [Ee]ast | [Ss]outh | [Nn]orth )[a-z ]*([A-Z0-9]\\w+\\b).*", "\\1 & \\3, Chicago, IL", description)

        if ', Chicago, IL' in description:
            counter += 1
            print counter
            try:
                time.sleep(2)
                georeference = geo.geocode(description, exactly_one=True)
                if '&' in georeference[0] :
                    c.execute("update tag set lat_long = PointFromText('POINT(%s %s)') where image_id = %s", (georeference[1][1], georeference[1][0], image_id))
            except (ValueError, GQueryError) :
                try:
                    print unicode(description)
                    print ''
                except:
                    description
            try:
                print unicode(description)
                print ''
            except:
                description

geo = geocoders.Google()    
try:
    time.sleep(2)
    georeference = geo.geocode(description, exactly_one=True)
except:
    print "woops"

c.close()
