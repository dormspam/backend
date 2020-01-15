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
                      "aaa", "ats", "dim sum", "drink"]),
    'CAREER': (1 << 3, ["career", "summer plans", "internship", "xfair", "recruiting"]),
    'FUNDRAISING': (1 << 4, ["donate"]),
    'APPLICATION': (1 << 5, ["apply", "deadline", "sign up", "audition", "join", "application"]),
    'PERFORMANCE': (1 << 6, ["orchestra", "shakespeare", "theatre", "theater", "tryout",
                             "audition", "muses", "serenade", "syncopasian", "ohms", "logarhythms", "chorallaries",
                             "symphony", "choir", "concert", "ensemble", "jazz", "resonance", "a capella", "toons",
                             "sing", "centrifugues", "dancetroupe", "adt", "asian dance team", "mocha moves",
                             "ridonkulous", "donk", "fixation", "bhangra", "roadkill", "vagina monologues", "24 hour show", "acappella", "admission", "ticket"]),
    'BOBA': (1 << 7, ["boba", "bubble tea", "kung fu tea", "kft", "teado", "tea do"]),
    'TALKS': (1 << 8, ["discussion", "q&a", "tech talk", "recruiting", "info session", "information session"
                       "infosession", "workshop", "research"]),
    'EECS-jobs-announce': (1 << 9, ["eecs-jobs-announce"]),
}

def parse_type(text):
    global CATEGORIES

    score = 0
    text = text.lower()
    for key in CATEGORIES:
        mod, keywords = CATEGORIES[key]
        if (any([re.search(f"\W{x}\W", text, flags=re.I) is not None for x in keywords])):
            score += mod
    if score == 0:
        return 1 # Will not classify this at all
    return score

if __name__ == "__main__":
    f = open("test_type.txt", "r")
    for l in f.readlines():
        print("****** " + l[:60].strip() + "... **********")
        for key in CATEGORIES:
            mod, keywords = CATEGORIES[key]
            if (any([re.search(f"\W{x}\W", l.lower().strip(), flags=re.I) is not None for x in keywords])):
                print(key)
