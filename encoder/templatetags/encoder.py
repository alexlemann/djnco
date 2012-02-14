import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

def link_seek(value):
    """
    Create a link for tokens like "23:41" or "2:32:77" in value.
    Split the string into tokens, then try to match a time regexp with the
        tokens. If it matches, replace the token with a link.
    """
    if not value:
        return None
    regexp = "((?P<hrs>\d?\d):)?(?P<mins>\d?\d):(?P<secs>\d\d)"
    tokens = re.split('([^\d:])', value)
    for i in range(len(tokens)):
        m = re.match(regexp, tokens[i])
        if m:
            hrs, mins, secs = m.group('hrs'), m.group('mins'), m.group('secs')
            time = int(mins)*60 + int(secs)
            if hrs:
                time += int(hrs)*60*60
                time_str = "%s:%s:%s" % (hrs, mins, secs)
                link = """<a class="seeklink" href="?time=%s" onClick="seek(%d);">%s</a>""" % (time_str, time, time_str)
                tokens[i] = tokens[i].replace(":".join((hrs,mins,secs)), link)
            else:
                time_str = "%s:%s" % (mins, secs)
                link = """<a class="seeklink" href="?time=%s" onClick="seek(%d);">%s</a>""" % (time_str, time, time_str)
                tokens[i] = tokens[i].replace(":".join((mins,secs)), link)
    return mark_safe(''.join(tokens))
register.filter('link_seek', link_seek)
