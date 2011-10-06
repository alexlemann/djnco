import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

def link_seek(value):
  if not value:
      return None
  for mins, secs in re.findall("(\d\d?):(\d\d)", value):
    time = int(mins)*60 + int(secs)
    link = """<a href="#" onClick="seek(%s);">%s:%s</a>""" % (str(time), mins, secs)
    value = value.replace(":".join((mins,secs)), link)
  return mark_safe(value)
register.filter('link_seek', link_seek)
