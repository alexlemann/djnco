import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

def link_seek(value):
    if not value:
        return None
    regexp = "((?P<hrs>\d?\d):)?(?P<mins>\d?\d):(?P<secs>\d\d)"
    for m in re.finditer(regexp, value):
        hrs, mins, secs = m.group('hrs'), m.group('mins'), m.group('secs')
        time = int(mins)*60 + int(secs)
        if hrs:
            time += int(hrs)*60*60
            time_str = "%s:%s:%s" % (hrs, mins, secs)
        else:
            time_str = "%s:%s" % (mins, secs)
        link = """<a class="seeklink" href="?time=%s" onClick="seek(%d);">%s</a>""" % (time_str, time, time_str)
        if hrs:
            value = value.replace(":".join((hrs,mins,secs)), link)
        else:
            value = value.replace(":".join((mins,secs)), link)
    return mark_safe(value)
register.filter('link_seek', link_seek)
