# Same as CalendarPage.tsx
# enum SortType {
#   ALL = 0,
#   FUNDRAISING = 1 << 1,
#   FOOD = 1 << 2,
#   CAREER = 1 << 3,
#   CLUB = 1 << 4,
#   APPLICATION = 1 << 5,
#   PERFORMANCE = 1 << 6
# }

def parse_type(text):
    text = text.lower()
    funcs = [is_performance, is_application, is_career, is_club, is_food, is_fundraising]
    return sum([f(text) for f in funcs])

def is_performance(text):
    perf_strings = ["ticket", "admission","a cappella","acappella", "concert"]
    def test():
        if (any([" " + x in text or "." + x in text or "\n" + x in text for x in test_strings])):
            return True
        return False
    if test():
        return 1 << 6
    return 0

def is_application(text):
    test_strings = ["apply", "deadline", "sign up"]
    def test():
        if (any([" " + x in text or "." + x in text or "\n" + x in text for x in test_strings])):
            return True
        return False
    if test():
        return 1 << 5
    return 0

def is_club(text):
    # TODO(kevinfang): whitelist by to sender
    test_strings = ["club", "student group", "cultural group"]
    def test():
        if (any([" " + x in text or "." + x in text or "\n" + x in text for x in test_strings])):
            return True
        return False
    if test():
        return 1 << 4
    return 0

def is_career(text):
    test_strings = ["career", "summer plans", "internship"]
    def test():
        if (any([" " + x in text or "." + x in text or "\n" + x in text for x in test_strings])):
            return True
        return False
    if test():
        return 1 << 3
    return 0

def is_food(text):
    test_strings = ["cookie", "food", "eat", "study break"]
    def test():
        if (any([" " + x in text or "." + x in text or "\n" + x in text for x in test_strings])):
            return True
        return False
    if test():
        return 1 << 2
    return 0

def is_fundraising(text):
    test_strings = ["donate"]
    def test():
        if (any([" " + x in text or "." + x in text or "\n" + x in text for x in test_strings])):
            return True
        return False
    if test():
        return 1 << 1
    return 0

if __name__ == "__main__":
    f = open("test_type.txt", "r")
    for l in f.readlines():
        print(l[:40].strip())
        funcs = [is_performance, is_application, is_career, is_club, is_food, is_fundraising]
        for f in funcs:
            if (f(l.lower().strip())):
                print(f.__name__)