import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

def link_seek(value):
  if not value:
      return None
  for mins, secs in set(re.findall("(\d\d?):(\d\d)", value)):
    time = int(mins)*60 + int(secs)
    link = """<a class="seeklink" href="?time=%s:%s" onClick="seek(%d);">%s:%s</a>""" % (mins, secs, time, mins, secs)
    value = value.replace(":".join((mins,secs)), link)
  return mark_safe(value)
register.filter('link_seek', link_seek)
