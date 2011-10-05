import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

def link_seek(value):
  if not value:
      return None
  for mins, secs in re.findall("(\d\d?):(\d\d)", value):
    time = int(mins)*60 + int(secs)
    value = value.replace(":".join((mins,secs)), '<a href="#" onClick="$f(\'player\').seek(%s);">%s:%s</a>' % ( str(time), mins, secs) )
  return mark_safe(value)
register.filter('link_seek', link_seek)
