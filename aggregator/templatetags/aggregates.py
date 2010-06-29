from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from django.utils.html import escape

import hashlib
import datetime

register = template.Library()

@register.filter
def show_aggregate(aggregate):
    '''Accepts some aggregate object (possibly, blog, blog comment, alert, or tweet),
    and render a custom view of it.'''
    template_name = "aggregates/%s.html" % aggregate.__class__.__name__
    t = template.loader.get_template(template_name)
    aggregate.klass=aggregate.__class__.__name__
    result = t.render(context=template.Context({'aggregate': aggregate}))
    return mark_safe(result)
    
@register.filter
def age(time):
    '''Given a datetime object, humanize it to one of:
    x seconds ago (up to 60 seconds)
    x minutes ago (up to 90 minutes)
    x hours ago (up to 24 hours)
    x days ago (up to 14 days)
    x weeks ago (up to six weeks)
    MMM DD, YYYY'''
    now = datetime.datetime.now()
    age = now - time
    if age.days > 42:
        return time.strftime("%B %d, %Y")
    if age.days > 14:
        return "%d weeks ago" % (age.days / 7)
    if age.days > 0:
        return "%d days ago" % (age.days)
    if age.seconds > 90 * 60:
        return "%d hours ago" % (age.seconds / 60 / 60)
    if age.seconds > 60:
        return "%d minutes ago" % (age.seconds / 60)
    return "%d seconds ago" % (age.seconds)

@register.filter
def human_time(value):
    if not isinstance(value, datetime.datetime):
        return value

    now = datetime.datetime.now()
    mins = int((now - value).seconds / 60)
    if mins == 1:
        return "1 minute ago"
    if mins < 60:
        return "%d minutes ago" % mins
    hours = int(round(mins / 60.0))
    if hours == 1:
        return "1 hour ago"
    if hours < 12:
        return "%d hours ago" % hours

    return value.strftime("at %I:%M %p on %b %d, %Y")

@register.simple_tag
def gravatar(email, size=32):
    digest = hashlib.new('md5', email.lower()).hexdigest()
    url = 'http://www.gravatar.com/avatar/%s?s=%s&d=identicon' % (digest, size)
    return """<img src="%s" height="%s" width="%s"/>""" % (escape(url), size, size)
