import re
# Same as CalendarPage.tsx
# enum SortType {
#   ALL = 0,
#   OTHER = 1 << 1,
#   FOOD = 1 << 2,
#   CAREER = 1 << 3,
#   FUNDRAISING = 1 << 4,
#   APPLICATION = 1 << 5,
#   PERFORMANCE = 1 << 6,
#   BOBA = 1 << 7,
#   TALKS = 1 << 8,
#   EECS = 1 << 9,
# }
CATEGORIES = {
    'FOOD': (1 << 2, ["cookie", "food", "eat", "study break", "boba", "bubble tea", "chicken", "bonchon", "bon chon", "bertucci",
                      "pizza", "sandwich", "leftover", "salad", "burrito", "dinner provided", "lunch provided", "breakfast provided",
                      "dinner included", "lunch included", "ramen", "kbbq", "dumplings", "waffles", "csc",
                      "aaa", "ats", "dim sum", "drink"],
             {
        "name": "Food",
        "id": "food",
        "description": "Breakfast, lunch, and dinner served",
        "color": "#EE6F6F"
    }),
    'CAREER': (1 << 3, ["career", "summer plans", "internship", "xfair", "recruiting"],
               {
        "name": "Career",
        "id": "career",
        "description": "Career and Recruiting events held by companies on campus",
        "color": "#459AF6"
    }),
    'FUNDRAISING': (1 << 4, ["donate", "donated", "donation"],
                    {
        "name": "Fundraising",
        "id": "fundraising",
        "description": "If you're looking to help a cause this is the way to go",
        "color": "#A16EE5"
    }),
    'APPLICATION': (1 << 5, [(2, ["apply", "application", "join"]), "deadline", "sign up", "audition", "application"],
                    {
        "name": "Applications",
        "id": "applications",
        "description": "Trying to join something or apply for anything?",
        "color": "#459AF6"
    }),
    'PERFORMANCE': (1 << 6, ["orchestra", "shakespeare", "theatre", "theater", "tryout",
                             "audition", "muses", "serenade", "syncopasian", "ohms", "logarhythms", "chorallaries",
                             "symphony", "choir", "concert", "ensemble", "jazz", "resonance", "a capella", "toons",
                             "sing", "centrifugues", "dancetroupe", "adt", "asian dance team", "mocha moves",
                             "ridonkulous", "donk", "fixation", "bhangra", "roadkill", "vagina monologues", "24 hour show", "acappella", "admission", "ticket"],
                    {
        "name": "Performance",
        "id": "performance",
        "description": "Dance, music, a capella, and other concerts and performances",
        "color": "#12DAA4"
    }),
    'BOBA': (1 << 7, ["boba", "bubble tea", "kung fu tea", "kft", "teado", "tea do"], {
        "name": "Boba",
        "id": "boba",
        "description": "Mouthwatering, scrumptious goodness",
        "color": "#F6B957"
    }),
    'TALKS': (1 << 8, ["discussion", "q&a", "tech talk", "recruiting", "info session", "information session"
                       "infosession", "workshop", "research"],
              {
        "name": "Talks",
        "id": "talks",
        "description": "Talks and short classes about anything you can imagine!",
        "color": "#73F23A"
    }),
    'EECS-jobs-announce': (1 << 9, ["eecs-jobs-announce"],
                           {
        "name": "EECS-jobs-announce",
        "id": "eecs",
        "description": "All events from the EECS-jobs-announce mailing list",
        "color": "#5A56EF"
    }),
    'SOCIAL': (1 << 10, ['party', 'karaoke'],
               {
        "name": "Social",
        "id": "social",
        "description": "Parties, karaoke nights, and food related outings",
        "color": "#25C8D3"
    })
}


def parse_type(text):
    global CATEGORIES

    score = 0
    text = text.lower()
    for key in CATEGORIES:
        mod, keywords, _ = CATEGORIES[key]
        for x in keywords:
            minreq = 1
            if (type(x) == tuple):
                minreq, x = x
            if minreq <= sum([re.search(f"\W{x}\W", text, flags=re.I) is not None]):
                score += mod
                break
    if score == 0:
        return 1  # Will not classify this at all
    return score


if __name__ == "__main__":
    f = open("test_type.txt", "r")
    for l in f.readlines():
        print("****** " + l[:60].strip() + "... **********")
        for key in CATEGORIES:
            mod, keywords, _ = CATEGORIES[key]
            if (any([re.search(f"\W{x}\W", l.lower().strip(), flags=re.I) is not None for x in keywords])):
                print(key)
