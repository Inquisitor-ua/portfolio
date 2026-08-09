from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from core.blocks import LinkBlock, SectionStreamBlock


class HomePage(Page):
    """The single top-level page of the site: a fixed hero band followed by
    an editor-composed stream of sections (about, experience, skills,
    projects, testimonials, contact...)."""

    role = models.CharField(
        max_length=140,
        blank=True,
        help_text='Shown under your name in the hero, e.g. "Full-Stack Developer".',
    )
    intro = RichTextField(
        blank=True,
        editor="simple",
        help_text="A short one or two sentence answer to ‘who am I, what do I do’.",
    )
    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_buttons = StreamField(
        [("button", LinkBlock())],
        blank=True,
        use_json_field=True,
        max_num=3,
        help_text='e.g. "View projects" and "Download CV".',
    )
    body = StreamField(SectionStreamBlock(), blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("role"),
                FieldPanel("intro"),
                FieldPanel("photo"),
                FieldPanel("hero_buttons"),
            ],
            heading="Hero",
        ),
        FieldPanel("body"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["projects.ProjectIndexPage"]

    class Meta:
        verbose_name = "Home page"
