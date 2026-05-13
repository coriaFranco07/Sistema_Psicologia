from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    request = context.get("request")
    if request is None:
        return ""

    query = request.GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            query.pop(key, None)
            continue
        query[key] = value

    encoded = query.urlencode()
    return f"?{encoded}" if encoded else ""
