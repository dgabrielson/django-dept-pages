# -*- coding: utf-8 -*-
"""
Activate in your template by putting
{% load unitpages_extras %}
near the top.

Available Filters:
startswith  - check if a string startswith a substring
mytrunk - truncate a string


Available Commands:
sitefile_url - provide an href to a sitefile object.
unitpage_url - provide an href to a unitpage by slug.
"""
#######################
from __future__ import print_function, unicode_literals

#######################
import os
import re

from django import template
from django.template import Context, Template
from django.urls import reverse
from django.utils.encoding import force_text, smart_str
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from ..models import Page, SiteFile

#####################################################################

register = template.Library()


#####################################################################


@register.filter
def startswith(string, start):
    """
    Returns <boolean> string.startswith(start)

    Usage: {% if string|startswith:"start" %} ... {% endif %}

    NOTE: no whitespace is allowed in the ``start`` argument.
        Also ``start`` might be a non-string object (or a lazy
        evaluation) so we cast it to be sure.
    """
    if not hasattr(string, "startswith"):
        return False
    return string.startswith(str(start))


startswith.is_safe = True


#####################################################################


@register.filter
def endswith(string, sub):
    """
    Returns <boolean> string.endswith(sub)

    Usage: {% if string|endswith:"sub" %} ... {% endif %}

    NOTE: no whitespace is allowed in the ``sub`` argument.
        Also ``sub`` might be a non-string object (or a lazy
        evaluation) so we cast it to be sure.
    """
    if not hasattr(string, "endswith"):
        return False
    return string.endswith(str(sub))


endswith.is_safe = True


#####################################################################


@register.filter
def mytrunc(string, length):
    """
    Returns a possibly truncated version of string.
    If string has been truncated, it will end with '...'
    (Like slice, but does some extra stuff.)

    Usage: {{ string|mytrunc:"20" }}

    """
    n = int(length)
    string = "{}".format(string)
    if n < len(string.strip()):
        return string[:n].strip() + "..."
    return string


mytrunc.is_safe = True


#####################################################################


class CurrentTimeNode(template.Node):
    def __init__(self, format_string):
        self.format_string = format_string

    def render(self, context):
        return now().strftime(self.format_string)


@register.tag(name="current_time")
def do_current_time(parser, token):
    """
    Example tag from the docs.
    http://docs.djangoproject.com/en/1.0/howto/custom-template-tags/#writing-the-compilation-function
    Usage:
        The time is {% current_time "%Y-%m-%d %I:%M %p" %}.

    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, format_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires a single argument" % token.contents.split()[0]
        )
    if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name
        )
    return CurrentTimeNode(format_string[1:-1])


#####################################################################

#####################################################################


class Model_Href_Node(template.Node):
    def __init__(self, tag_name, model, slug, literal, context_name):
        self.tag_name = tag_name
        self.model = model
        self.slug = slug
        self.literal = literal
        self.context_name = context_name

    def render(self, context):
        if self.literal:
            slug = self.slug
        else:
            if self.slug not in context:
                raise template.TemplateSyntaxError(
                    "%r tag: variable %r not defined in this block"
                    % (self.tag_name, self.slug)
                )
            slug = context[self.slug]

        try:
            if self.model == Page:
                url = slug
                if not url.startswith("/"):
                    url = "/" + url
                if not url.endswith("/"):
                    url = url + "/"
                try:
                    o = self.model.objects.get(active=True, url=url)
                except Page.DoesNotExist:
                    o = self.model.objects.get(active=True, url__endswith=url)
            else:
                o = self.model.objects.get(active=True, slug=slug)
            url = o.get_absolute_url()
        except self.model.DoesNotExist:
            url = ""

        if self.context_name is not None:
            context[self.context_name] = url
            return ""
        else:
            return url


def do_model_href(model, parser, token):
    """
    Usage:
        {% tag "slug" %}
        -or-
        {% tag "slug" as link_url %}

    The model must have an active field, and a slug field, as well as defining
    get_absolute_url().
    """
    token_contents = token.split_contents()

    tag_name = token_contents[0]

    if len(token_contents) < 2:
        raise template.TemplateSyntaxError("%r tag requires an argument" % tag_name)

    slug = token_contents[1]
    if slug[0] in "'\"":
        if slug[0] != slug[-1]:
            raise template.TemplateSyntaxError(
                "mismatched quotes for %r tag" % tag_name
            )
        slug = slug[1:-1]
        literal = True
    else:
        literal = False

    if len(token_contents) == 2:
        return Model_Href_Node(tag_name, model, slug, literal, None)

    if len(token_contents) == 4:
        if token_contents[2] != "as":
            raise template.TemplateSyntaxError("invalid syntax for %r tag" % tag_name)
        context_name = token_contents[3]
        return Model_Href_Node(tag_name, model, slug, literal, context_name)

    raise template.TemplateSyntaxError("%r tag: invalid syntax" % tag_name)


#####################################################################


@register.tag(name="unitpage_url")
def do_unitpage_href(parser, token):
    """
    Usage:
        {% unitpage_url "undergraduate" %}
        -or-
        {% unitpage_url "undergraduate" as link_url %}
    """
    return do_model_href(Page, parser, token)


#####################################################################


@register.tag(name="sitefile_url")
def do_sitefile_href(parser, token):
    """
    Usage:
        {% sitefile_url "undergraduate" %}
        -or-
        {% sitefile_url "undergraduate" as link_url %}
    """
    return do_model_href(SiteFile, parser, token)


#####################################################################


@register.inclusion_tag("unitpages/includes/breadcrumb.html")
def unitpage_breadcrumb(url):
    try:
        o = Page.objects.get(active=True, url=url)
    except Page.DoesNotExist:
        return {}
    else:
        return {"url": o.get_absolute_url(), "title": o.title}


#####################################################################


@register.simple_tag(takes_context=True)
def unitpage_title(context, url, titlevar, urlvar=None):
    context[titlevar] = ""
    if urlvar is not None:
        context[urlvar] = ""
    try:
        o = Page.objects.get(active=True, url=url)
    except Page.DoesNotExist:
        pass
    else:
        context[titlevar] = o.get_short_title_display()
        if urlvar is not None:
            context[urlvar] = o.get_absolute_url()
    return ""


#####################################################################


@register.simple_tag(takes_context=True)
def unitpage_load_page(context, url, save_as=None):
    result = ""
    try:
        o = Page.objects.get(active=True, url=url)
    except Page.DoesNotExist:
        pass
    else:
        if save_as is not None:
            context[save_as] = o
        else:
            result = o.content
    return result


#####################################################################


@register.filter(name="prerender")
def render_as_template(text, context=None):
    """
    {% page.content|prerender %}
    """
    if context is None:
        context = Context({})
    this_file = os.path.splitext(os.path.split(__file__)[-1])[0]
    template_text = "{% load " + this_file + " %}\n" + text
    t = Template(template_text)
    output = t.render(context)
    return output


render_as_template.is_safe = True


#####################################################################


@register.simple_tag(name="prerender_with_context", takes_context=True)
def render_as_template_with_context(context, text, save_as=None, **kwargs):
    """
    {% prerender_with_context page.content %}{# almost equivalent to page.content|prerender #}
    {% prerender_with_context page.content "my_content" %}
    {% prerender_with_context page.content "my_content" foo="bar" ... %}
    """
    local_context = Context(context)
    if kwargs:
        local_context.update(kwargs)
    render = render_as_template(text, local_context)
    if save_as is not None:
        context[save_as] = render
        return ""
    return render


#####################################################################
