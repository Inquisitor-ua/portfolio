from django.db import models
from django.utils.functional import cached_property

from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index

from core.blocks import ContentStreamBlock

STATUS_CHOICES = [
    ("live", "Live"),
    ("in_progress", "In progress"),
    ("archived", "Archived"),
]


class ProjectIndexPage(Page):
    """Lists all projects. Its only child pages are ``ProjectPage``s."""

    intro = RichTextField(blank=True, editor="simple")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["projects.ProjectPage"]

    class Meta:
        verbose_name = "Projects index page"

    def get_children_projects(self):
        return (
            ProjectPage.objects.child_of(self)
            .live()
            .order_by("-first_published_at")
        )


class ProjectPage(Page):
    """A single project — a case-study page plus the details needed to list
    it as a card (summary, cover image, tech stack, link to the deployed
    project on its own subdomain)."""

    summary = models.CharField(
        max_length=240,
        help_text="Short description shown on project cards.",
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    subdomain_url = models.URLField(
        "live URL",
        help_text="Where the deployed project lives, e.g. https://myapp.example.com",
    )
    repo_url = models.URLField("repository URL", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="live")
    featured = models.BooleanField(
        default=False,
        help_text="Featured projects are shown first in the projects section.",
    )
    technologies = ParentalManyToManyField(
        "core.Technology", blank=True, related_name="projects"
    )
    date_started = models.DateField(null=True, blank=True)
    date_completed = models.DateField(null=True, blank=True)
    body = StreamField(ContentStreamBlock(), blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("summary"),
        FieldPanel("cover_image"),
        MultiFieldPanel(
            [
                FieldPanel("subdomain_url"),
                FieldPanel("repo_url"),
                FieldPanel("status"),
                FieldPanel("featured"),
                FieldPanel("technologies"),
                FieldPanel("date_started"),
                FieldPanel("date_completed"),
            ],
            heading="Project details",
        ),
        FieldPanel("body"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("summary"),
    ]

    parent_page_types = ["projects.ProjectIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Project page"

    @cached_property
    def status_label(self):
        return dict(STATUS_CHOICES).get(self.status, self.status)

    @cached_property
    def tech_list(self):
        return [tech.name for tech in self.technologies.all()]
