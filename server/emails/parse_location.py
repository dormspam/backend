import re

LOCATIONS = ["Baker Dining", "Baker D", "MacGregor Dining", "MacGregor Dance Studio", "McCormick Dance Studio",
"Burton Conner Porter Room", "BC Porter Room", "Porter Room", "McCormick Country Kitchen", "Lobby 7",
"Lobby 10", "Lobby 13", "T-club", "Johnson Ice Rink", "Z-center", "Z center", "Kresge Little Theatre",
"Little Kresge", "Kresge Auditorium", "Kresge", "Stata Lobby", "Stata", "Mezzanine Lounge", "Coffeehouse Lounge",
"Lobdell", "Student Center", "Banana Lounge", "Talbot Lounge", "Talbot", "McDermott Court", "Sidney Pacific",
"Private Dining Room", "PDR", "Athena Cluster", "Walker", "D-Lab", "DuPont Wrestling Room", "DuPont",
"Building 56", "Hei La Moon", "E51", "Media Lab", "E62"]


def valid_location_is(location):
    location = location.split('-')[0]
    return len([i for i in location if i in '1234567890']) <= 2 and len(location) <= 3


def parse_location(text):
    x = parse_all_locations(text)
    if len(x) == 0:
        return None
    else:
        return x[0].strip()

def parse_all_locations(text):
    x = re.findall("[ \n][A-Z0-9]+-[0-9][0-9][0-9]", text)
    x += re.findall("32-G[0-9][0-9][0-9]", text)
    x += re.findall("32-D[0-9][0-9][0-9]", text)
    locs = []
    for location in LOCATIONS:
        matches = re.findall(location, text, flags=re.I)
        if len(matches) != 0:
            locs.append(location)
    locs.extend([i for i in x if valid_location_is(i)])
    return locs

if __name__ == "__main__":
    f = open("test_locations.txt", "r")
    for l in f.readlines():
        print("***** " + l[:70].strip() + "... *****")
        print(parse_location(l.strip()))
