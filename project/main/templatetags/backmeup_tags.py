from django import template
import datetime
register = template.Library()

@register.filter(name='to_date')
def to_date(value):
	try:
		ts=float(value)
	except ValueError:
		return None
	return datetime.datetime.fromtimestamp(ts)
