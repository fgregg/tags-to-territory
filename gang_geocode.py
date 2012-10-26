import MySQLdb
from geopy import geocoders
from geopy.geocoders.google import GQueryError
from string import Template

def addressOrIntersection(location) :
    place = None
    
    street_address = Template("$street_0, $city $state")
    intersection = Template("$street_0 & $street_1, $city $state")

    if location['xstreet0'] :
        # Sometimes street addresses are written out, particularly
        # 'One' and sometimes 'Two.' Right now we are only catching
        # addresses that start with a sequence of numbers a space and
        # something that is not a number or whitespace (ideally an
        # letter.
        if re.compile('\d+ [\D\W]').match(location['xstreet0']) :
            place = street_address.substitute(street_0 = location['xstreet0'],
                                              city = "Chicago",
                                              state = "IL")
        else :
            if location['xstreet1'] and location['xstreet1'] != location['xstreet0'] :
                # Likely fertile place for improvement
                xstreet_splitter = re.compile('(.+)( and |/)(.+)')
                xstreet_split = xstreet_splitter.findall(location['xstreet1'])
                if xstreet_split :
                    xstreet0 = xstreet_split[0][0].strip()
                    xstreet1 = xstreet_split[0][2].strip()
                else :
                    xstreet0 = location['xstreet0']
                    xstreet1 = location['xstreet1']
                xstreet0 = xstreet0.title()
                xstreet1 = xstreet1.title()
                place = intersection.substitute(street_0 = xstreet0,
                                                street_1 = xstreet1,
                                                city = "Chicago",
                                                state = "IL"
                                                )
    return place


test_text = ["Grand/Keeler st. -Insane Ashland Vikings' hood",
             "K Town AVN.",
             ]

def extractPlace(text) :
    intersection = re.compile('([a-zA-Z]+)\B\W([a-zA-Z]+).*')

    print intersection.findall(text)

extractPlace(test_text[0])
