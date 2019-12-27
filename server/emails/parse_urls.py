import re

def parse_urls(text):
    """Parses URL from text
    
    Arguments:
        text {string} -- string needing parsing
    
    Returns:
        (string) -- url
    """
    search = re.search("(?P<url>https?://[^\s>]+)", text)
    if search:
        return search.group("url")
    else:
        return None

def is_form(text):
    return "form" in text

if __name__ == "__main__":
    tests = ["Hey check out this https://forms.gle/8G9Vw1qeCLHH7U8f7", "not a google form https://imswimmer.com", "dum url <https://asdf.com>"]
    for test in tests:
        print(test)
        print(parse_urls(test))