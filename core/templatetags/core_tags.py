from django import template

register = template.Library()


@register.inclusion_tag("includes/icon.html")
def icon(name, size=24, css_class=""):
    """Render an inline SVG icon from the shared sprite.

    Usage: {% icon "github" %} or {% icon "arrow-right" size=16 css_class="btn__icon" %}
    """
    return {"name": name, "size": size, "css_class": css_class}


@register.simple_tag
def current_year():
    from django.utils import timezone

    return timezone.now().year
