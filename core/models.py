from django.db import models

from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.snippets.models import register_snippet

from core.blocks import LinkBlock, SocialLinkBlock


@register_snippet
class Technology(models.Model):
    """A single technology/tool badge — used in the tech grid, timeline and
    project pages."""

    name = models.CharField(max_length=60)
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="A square logo/mark, ideally an SVG or transparent PNG.",
    )
    url = models.URLField(blank=True, help_text="The technology's homepage.")
    category = models.CharField(
        max_length=60,
        blank=True,
        help_text='e.g. "Backend", "Frontend", "DevOps".',
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("logo"),
        FieldPanel("url"),
        FieldPanel("category"),
    ]

    class Meta:
        ordering = ["category", "name"]
        verbose_name_plural = "Technologies"

    def __str__(self):
        return self.name


@register_snippet
class Testimonial(models.Model):
    """A short quote from a colleague or client, used in the testimonials
    block."""

    name = models.CharField(max_length=120)
    role = models.CharField(max_length=140, blank=True)
    company = models.CharField(max_length=140, blank=True)
    quote = models.TextField()
    avatar = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("company"),
        FieldPanel("quote"),
        FieldPanel("avatar"),
    ]

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


@register_setting(icon="site")
class SiteBrandingSettings(BaseSiteSetting):
    """Site-wide identity, editable from Settings > Site branding."""

    site_name = models.CharField(max_length=80, default="Portfolio")
    tagline = models.CharField(
        max_length=160,
        blank=True,
        help_text="Short line shown in the browser tab / share previews.",
    )
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Shown in the header. Falls back to the site name if empty.",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    social_share_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Default image used when pages are shared, unless a page sets its own.",
    )

    panels = [
        FieldPanel("site_name"),
        FieldPanel("tagline"),
        FieldPanel("logo"),
        FieldPanel("favicon"),
        FieldPanel("social_share_image"),
    ]

    class Meta:
        verbose_name = "Site branding"


@register_setting(icon="list-ul")
class NavigationSettings(BaseSiteSetting, ClusterableModel):
    """The header navigation and footer note, editable from Settings >
    Navigation."""

    primary_links = StreamField(
        [("link", LinkBlock())],
        blank=True,
        use_json_field=True,
        help_text="Links shown in the main site header.",
    )
    footer_note = models.CharField(
        max_length=200,
        blank=True,
        help_text='Short line shown in the footer, e.g. "Built with Django & Wagtail."',
    )

    panels = [
        FieldPanel("primary_links"),
        FieldPanel("footer_note"),
    ]

    class Meta:
        verbose_name = "Navigation"


@register_setting(icon="mail")
class ContactSettings(BaseSiteSetting, ClusterableModel):
    """Contact details and social links, editable from Settings > Contact."""

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    availability_available = models.BooleanField(
        default=True,
        verbose_name="Currently available",
        help_text="Toggles the availability indicator shown in the contact section.",
    )
    availability_text = models.CharField(
        max_length=140,
        blank=True,
        default="Available for new opportunities",
    )
    cv_document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="CV / résumé",
    )
    social_links = StreamField(
        [("link", SocialLinkBlock())],
        blank=True,
        use_json_field=True,
        help_text="Social / profile links shown in the footer and contact section.",
    )

    panels = [
        FieldPanel("email"),
        FieldPanel("phone"),
        FieldPanel("location"),
        FieldPanel("availability_available"),
        FieldPanel("availability_text"),
        FieldPanel("cv_document"),
        FieldPanel("social_links"),
    ]

    class Meta:
        verbose_name = "Contact"
