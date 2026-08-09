"""
StreamField block library.

Two layers:

* ``ContentStreamBlock`` — the building blocks that go *inside* a section
  (text, images, stats, timeline, skills, code, …).
* ``SectionStreamBlock`` — full-width page sections that wrap content blocks and
  control heading, background and layout. Page bodies use this one, so an editor
  can reorder or remove whole sections of the site from the Wagtail admin.
"""

from django.utils.functional import cached_property
from wagtail import blocks
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock

# --------------------------------------------------------------------------- #
# Shared choices
# --------------------------------------------------------------------------- #

BACKGROUND_CHOICES = [
    ("none", "None — page background"),
    ("tint", "Subtle tint"),
    ("panel", "Raised panel"),
    ("gradient", "Accent gradient"),
    ("dark", "Always dark"),
]

WIDTH_CHOICES = [
    ("narrow", "Narrow — comfortable reading width"),
    ("normal", "Normal"),
    ("wide", "Wide"),
    ("full", "Full bleed"),
]

ALIGN_CHOICES = [
    ("start", "Left"),
    ("center", "Centre"),
]

BUTTON_STYLE_CHOICES = [
    ("primary", "Primary — solid accent"),
    ("secondary", "Secondary — outlined"),
    ("ghost", "Ghost — text only"),
]

TONE_CHOICES = [
    ("info", "Info"),
    ("success", "Success"),
    ("warning", "Warning"),
    ("accent", "Accent"),
]

ICON_CHOICES = [
    ("", "No icon"),
    ("arrow-up-right", "Arrow (up-right)"),
    ("arrow-right", "Arrow (right)"),
    ("arrow-down", "Arrow (down)"),
    ("download", "Download"),
    ("mail", "Mail"),
    ("phone", "Phone"),
    ("map-pin", "Location pin"),
    ("calendar", "Calendar"),
    ("briefcase", "Briefcase"),
    ("graduation", "Graduation cap"),
    ("code", "Code"),
    ("link", "Link"),
    ("globe", "Globe"),
    ("external", "External window"),
    ("layers", "Layers"),
    ("spark", "Spark"),
    ("check", "Check"),
    ("search", "Search"),
    ("github", "GitHub"),
    ("gitlab", "GitLab"),
    ("linkedin", "LinkedIn"),
    ("x", "X / Twitter"),
    ("telegram", "Telegram"),
]


# --------------------------------------------------------------------------- #
# Links
# --------------------------------------------------------------------------- #

class LinkStructValue(blocks.StructValue):
    """Resolves the three possible link targets down to a single href."""

    @cached_property
    def href(self):
        page = self.get("page")
        document = self.get("document")
        url = (self.get("external_url") or "").strip()
        anchor = (self.get("anchor") or "").strip().lstrip("#")

        if page and page.live:
            base = page.url or ""
        elif document:
            base = document.url
        elif url:
            base = url
        elif anchor:
            return f"#{anchor}"
        else:
            return ""

        if anchor and base:
            return f"{base}#{anchor}"
        return base

    @cached_property
    def text(self):
        label = (self.get("label") or "").strip()
        if label:
            return label
        page = self.get("page")
        if page:
            return page.title
        document = self.get("document")
        if document:
            return document.title
        return self.get("external_url") or ""

    @cached_property
    def is_external(self):
        return bool((self.get("external_url") or "").strip()) and not self.get("page")


class LinkBlock(blocks.StructBlock):
    """A link that can point at a page, a document, a URL, or an on-page anchor."""

    label = blocks.CharBlock(
        required=False,
        max_length=80,
        help_text="Leave blank to use the linked page's title.",
    )
    page = blocks.PageChooserBlock(required=False, label="Internal page")
    external_url = blocks.URLBlock(
        required=False,
        label="External URL",
        help_text="Use this for project subdomains, e.g. https://myapp.example.com",
    )
    document = DocumentChooserBlock(required=False, label="Document (e.g. your CV)")
    anchor = blocks.CharBlock(
        required=False,
        max_length=60,
        help_text='Jump to a section on the target page, e.g. "contact".',
    )
    style = blocks.ChoiceBlock(
        choices=BUTTON_STYLE_CHOICES, default="primary", required=True
    )
    icon = blocks.ChoiceBlock(choices=ICON_CHOICES, default="", required=False)
    open_in_new_tab = blocks.BooleanBlock(required=False, default=False)

    class Meta:
        icon = "link"
        label = "Link"
        value_class = LinkStructValue
        form_classname = "struct-block link-block"


SOCIAL_PLATFORM_CHOICES = [
    ("github", "GitHub"),
    ("gitlab", "GitLab"),
    ("linkedin", "LinkedIn"),
    ("x", "X / Twitter"),
    ("telegram", "Telegram"),
    ("instagram", "Instagram"),
    ("facebook", "Facebook"),
    ("youtube", "YouTube"),
    ("dribbble", "Dribbble"),
    ("behance", "Behance"),
    ("codepen", "CodePen"),
    ("stackoverflow", "Stack Overflow"),
    ("medium", "Medium"),
    ("devto", "DEV Community"),
    ("mastodon", "Mastodon"),
    ("discord", "Discord"),
    ("bluesky", "Bluesky"),
    ("reddit", "Reddit"),
]


class SocialLinkBlock(blocks.StructBlock):
    """A single social/profile link, rendered with its brand icon."""

    platform = blocks.ChoiceBlock(choices=SOCIAL_PLATFORM_CHOICES, required=True)
    url = blocks.URLBlock(required=True)
    label = blocks.CharBlock(
        required=False,
        max_length=60,
        help_text="Leave blank to use the platform name.",
    )

    class Meta:
        icon = "link"
        label = "Social link"


class ButtonRowBlock(blocks.StructBlock):
    links = blocks.ListBlock(LinkBlock(), min_num=1, max_num=4, label="Buttons")
    align = blocks.ChoiceBlock(choices=ALIGN_CHOICES, default="start", required=True)

    class Meta:
        icon = "link"
        label = "Buttons"
        template = "core/blocks/button_row.html"


# --------------------------------------------------------------------------- #
# Text & media
# --------------------------------------------------------------------------- #

class HeadingBlock(blocks.StructBlock):
    text = blocks.CharBlock(max_length=180)
    level = blocks.ChoiceBlock(
        choices=[("h2", "Heading 2"), ("h3", "Heading 3"), ("h4", "Heading 4")],
        default="h3",
    )
    anchor = blocks.CharBlock(
        required=False,
        max_length=60,
        help_text="Optional id so this heading can be linked to directly.",
    )

    class Meta:
        icon = "title"
        label = "Heading"
        template = "core/blocks/heading.html"


class ParagraphBlock(blocks.RichTextBlock):
    class Meta:
        icon = "pilcrow"
        label = "Rich text"
        template = "core/blocks/paragraph.html"


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alt_text = blocks.CharBlock(
        required=False,
        max_length=200,
        help_text="Describe the image for screen readers. Falls back to the "
        "image's own title.",
    )
    caption = blocks.CharBlock(required=False, max_length=250)
    width = blocks.ChoiceBlock(choices=WIDTH_CHOICES, default="normal")
    rounded = blocks.BooleanBlock(required=False, default=True, label="Rounded corners")
    link = LinkBlock(required=False)

    class Meta:
        icon = "image"
        label = "Image"
        template = "core/blocks/image.html"


class GalleryBlock(blocks.StructBlock):
    images = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("image", ImageChooserBlock()),
                ("caption", blocks.CharBlock(required=False, max_length=250)),
            ]
        ),
        min_num=1,
        label="Images",
    )
    columns = blocks.ChoiceBlock(
        choices=[("2", "2 columns"), ("3", "3 columns"), ("4", "4 columns")],
        default="3",
    )

    class Meta:
        icon = "image"
        label = "Image gallery"
        template = "core/blocks/gallery.html"


class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock(rows=3)
    attribution = blocks.CharBlock(required=False, max_length=120)
    role = blocks.CharBlock(
        required=False, max_length=140, help_text="Job title and/or company."
    )
    avatar = ImageChooserBlock(required=False)

    class Meta:
        icon = "openquote"
        label = "Quote"
        template = "core/blocks/quote.html"


class CodeBlock(blocks.StructBlock):
    language = blocks.ChoiceBlock(
        choices=[
            ("python", "Python"),
            ("javascript", "JavaScript"),
            ("html", "HTML"),
            ("css", "CSS"),
            ("bash", "Shell"),
            ("json", "JSON"),
            ("yaml", "YAML"),
            ("sql", "SQL"),
            ("text", "Plain text"),
        ],
        default="python",
    )
    filename = blocks.CharBlock(required=False, max_length=120)
    code = blocks.TextBlock(rows=12)

    class Meta:
        icon = "code"
        label = "Code snippet"
        template = "core/blocks/code.html"


class CalloutBlock(blocks.StructBlock):
    tone = blocks.ChoiceBlock(choices=TONE_CHOICES, default="info")
    icon = blocks.ChoiceBlock(choices=ICON_CHOICES, default="spark", required=False)
    title = blocks.CharBlock(required=False, max_length=140)
    text = blocks.RichTextBlock(editor="simple")

    class Meta:
        icon = "help"
        label = "Callout"
        template = "core/blocks/callout.html"


class DividerBlock(blocks.StructBlock):
    style = blocks.ChoiceBlock(
        choices=[("line", "Line"), ("dots", "Dots"), ("space", "Empty space")],
        default="line",
    )

    class Meta:
        icon = "horizontalrule"
        label = "Divider"
        template = "core/blocks/divider.html"


# --------------------------------------------------------------------------- #
# Résumé-specific blocks
# --------------------------------------------------------------------------- #

class StatsBlock(blocks.StructBlock):
    items = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("value", blocks.CharBlock(max_length=12, help_text='e.g. "8" or "120"')),
                (
                    "suffix",
                    blocks.CharBlock(
                        required=False, max_length=6, help_text='e.g. "+" or "k"'
                    ),
                ),
                ("label", blocks.CharBlock(max_length=60)),
            ]
        ),
        min_num=2,
        max_num=6,
        label="Figures",
    )
    animate = blocks.BooleanBlock(
        required=False, default=True, help_text="Count up when scrolled into view."
    )

    class Meta:
        icon = "table"
        label = "Key figures"
        template = "core/blocks/stats.html"


class TimelineBlock(blocks.StructBlock):
    """Work history / education — the backbone of a CV page."""

    entries = blocks.ListBlock(
        blocks.StructBlock(
            [
                (
                    "period",
                    blocks.CharBlock(
                        max_length=60, help_text='e.g. "2022 — present"'
                    ),
                ),
                ("title", blocks.CharBlock(max_length=140, label="Role or qualification")),
                (
                    "organisation",
                    blocks.CharBlock(required=False, max_length=140),
                ),
                ("organisation_url", blocks.URLBlock(required=False)),
                ("location", blocks.CharBlock(required=False, max_length=120)),
                ("description", blocks.RichTextBlock(editor="simple", required=False)),
                (
                    "technologies",
                    blocks.ListBlock(
                        SnippetChooserBlock("core.Technology"),
                        required=False,
                        label="Technologies used",
                    ),
                ),
                ("current", blocks.BooleanBlock(required=False, default=False)),
            ]
        ),
        min_num=1,
        label="Entries",
    )
    icon = blocks.ChoiceBlock(choices=ICON_CHOICES, default="briefcase", required=False)

    class Meta:
        icon = "list-ul"
        label = "Timeline (experience / education)"
        template = "core/blocks/timeline.html"


class SkillsBlock(blocks.StructBlock):
    """Grouped skills with optional proficiency — rendered by a Vue component."""

    groups = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("name", blocks.CharBlock(max_length=60, label="Group name")),
                (
                    "skills",
                    blocks.ListBlock(
                        blocks.StructBlock(
                            [
                                ("name", blocks.CharBlock(max_length=60)),
                                (
                                    "level",
                                    blocks.IntegerBlock(
                                        min_value=1,
                                        max_value=5,
                                        default=4,
                                        help_text="1 = learning, 5 = expert.",
                                    ),
                                ),
                                (
                                    "note",
                                    blocks.CharBlock(required=False, max_length=120),
                                ),
                            ]
                        ),
                        min_num=1,
                    ),
                ),
            ]
        ),
        min_num=1,
        label="Skill groups",
    )
    show_levels = blocks.BooleanBlock(
        required=False, default=True, help_text="Show the proficiency meters."
    )

    class Meta:
        icon = "list-ul"
        label = "Skills matrix"
        template = "core/blocks/skills.html"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["skills_payload"] = [
            {
                "name": group["name"],
                "skills": [
                    {
                        "name": skill["name"],
                        "level": skill["level"],
                        "note": skill["note"],
                    }
                    for skill in group["skills"]
                ],
            }
            for group in value["groups"]
        ]
        return context


class TechGridBlock(blocks.StructBlock):
    technologies = blocks.ListBlock(
        SnippetChooserBlock("core.Technology"), min_num=1, label="Technologies"
    )
    size = blocks.ChoiceBlock(
        choices=[("sm", "Small"), ("md", "Medium"), ("lg", "Large")], default="md"
    )

    class Meta:
        icon = "cogs"
        label = "Technology badges"
        template = "core/blocks/tech_grid.html"


class FeatureListBlock(blocks.StructBlock):
    items = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("icon", blocks.ChoiceBlock(choices=ICON_CHOICES, default="check", required=False)),
                ("title", blocks.CharBlock(max_length=120)),
                ("text", blocks.RichTextBlock(editor="simple", required=False)),
                ("link", LinkBlock(required=False)),
            ]
        ),
        min_num=1,
        label="Items",
    )
    columns = blocks.ChoiceBlock(
        choices=[("1", "1 column"), ("2", "2 columns"), ("3", "3 columns")],
        default="3",
    )

    class Meta:
        icon = "list-ul"
        label = "Feature cards"
        template = "core/blocks/feature_list.html"


class TestimonialsBlock(blocks.StructBlock):
    testimonials = blocks.ListBlock(
        SnippetChooserBlock("core.Testimonial"), min_num=1, label="Testimonials"
    )
    columns = blocks.ChoiceBlock(
        choices=[("1", "1 column"), ("2", "2 columns"), ("3", "3 columns")],
        default="2",
    )

    class Meta:
        icon = "openquote"
        label = "Testimonials"
        template = "core/blocks/testimonials.html"


# --------------------------------------------------------------------------- #
# Content stream — what can appear inside a section
# --------------------------------------------------------------------------- #

class BaseContentStreamBlock(blocks.StreamBlock):
    """Every content block except ``columns`` — used inside a column so that
    columns cannot be nested inside each other."""

    heading = HeadingBlock()
    paragraph = ParagraphBlock()
    buttons = ButtonRowBlock()
    image = ImageBlock()
    gallery = GalleryBlock()
    quote = QuoteBlock()
    code = CodeBlock()
    callout = CalloutBlock()
    stats = StatsBlock()
    timeline = TimelineBlock()
    skills = SkillsBlock()
    tech_grid = TechGridBlock()
    features = FeatureListBlock()
    testimonials = TestimonialsBlock()
    table = TableBlock(template="core/blocks/table.html")
    embed = EmbedBlock(
        label="Embed (YouTube, Vimeo, CodePen …)",
        template="core/blocks/embed.html",
    )
    divider = DividerBlock()

    class Meta:
        required = False


class ColumnsBlock(blocks.StructBlock):
    """Two side-by-side content columns."""

    left = BaseContentStreamBlock(label="Left column")
    right = BaseContentStreamBlock(label="Right column")
    ratio = blocks.ChoiceBlock(
        choices=[
            ("1-1", "Equal"),
            ("2-1", "Wider left"),
            ("1-2", "Wider right"),
        ],
        default="1-1",
    )
    vertical_align = blocks.ChoiceBlock(
        choices=[("start", "Top"), ("center", "Centre")], default="start"
    )

    class Meta:
        icon = "duplicate"
        label = "Two columns"
        template = "core/blocks/columns.html"


class ContentStreamBlock(BaseContentStreamBlock):
    """The full content palette: everything above, plus two-column layouts."""

    columns = ColumnsBlock()

    class Meta:
        required = False


# --------------------------------------------------------------------------- #
# Section stream — what a page body is made of
# --------------------------------------------------------------------------- #

class SectionBlock(blocks.StructBlock):
    """A titled, full-width band of the page."""

    eyebrow = blocks.CharBlock(
        required=False,
        max_length=60,
        help_text='Small label above the heading, e.g. "About".',
    )
    heading = blocks.CharBlock(required=False, max_length=180)
    intro = blocks.RichTextBlock(editor="simple", required=False)
    content = ContentStreamBlock()
    width = blocks.ChoiceBlock(choices=WIDTH_CHOICES, default="normal")
    align = blocks.ChoiceBlock(choices=ALIGN_CHOICES, default="start", label="Heading alignment")
    background = blocks.ChoiceBlock(choices=BACKGROUND_CHOICES, default="none")
    anchor = blocks.CharBlock(
        required=False,
        max_length=60,
        help_text='Used for in-page navigation, e.g. "about". Also lets this '
        "section appear in the page's on-page menu.",
    )
    show_in_page_nav = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="List this section in the sticky on-page navigation "
        "(requires an anchor and a heading).",
    )

    class Meta:
        icon = "doc-full"
        label = "Section"
        template = "core/blocks/section.html"


class ProjectsSectionBlock(blocks.StructBlock):
    """Pulls project pages into any page, with an optional Vue filter UI."""

    eyebrow = blocks.CharBlock(required=False, max_length=60, default="Work")
    heading = blocks.CharBlock(required=False, max_length=180, default="Selected projects")
    intro = blocks.RichTextBlock(editor="simple", required=False)
    source = blocks.ChoiceBlock(
        choices=[
            ("featured", "Featured projects (newest first)"),
            ("latest", "Latest projects"),
            ("manual", "Hand-picked projects"),
        ],
        default="featured",
    )
    projects = blocks.ListBlock(
        blocks.PageChooserBlock(page_type="projects.ProjectPage"),
        required=False,
        label="Hand-picked projects",
        help_text='Only used when the source is "Hand-picked".',
    )
    limit = blocks.IntegerBlock(
        default=6, min_value=1, max_value=24, help_text="Maximum number to show."
    )
    layout = blocks.ChoiceBlock(
        choices=[
            ("grid", "Card grid"),
            ("list", "Detailed list"),
            ("compact", "Compact rows"),
        ],
        default="grid",
    )
    show_filters = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Add the interactive search and technology filters (Vue).",
    )
    cta = LinkBlock(required=False, label="Call to action")
    background = blocks.ChoiceBlock(choices=BACKGROUND_CHOICES, default="none")
    anchor = blocks.CharBlock(required=False, max_length=60, default="work")
    show_in_page_nav = blocks.BooleanBlock(required=False, default=True)

    class Meta:
        icon = "folder-open-inverse"
        label = "Projects section"
        template = "core/blocks/projects_section.html"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        # Imported lazily to avoid a circular import: projects.models imports
        # ContentStreamBlock from this module.
        from projects.models import ProjectPage

        source = value["source"]
        limit = value["limit"]

        if source == "manual":
            pages = [
                page.specific
                for page in value["projects"]
                if page and page.live
            ]
        else:
            queryset = ProjectPage.objects.live().public()
            if source == "featured":
                queryset = queryset.filter(featured=True)
            pages = list(queryset.order_by("-first_published_at")[:limit])

        context["resolved_projects"] = pages[:limit]
        return context


class ContactSectionBlock(blocks.StructBlock):
    """Renders the contact details held in Wagtail settings, plus a CTA."""

    eyebrow = blocks.CharBlock(required=False, max_length=60, default="Contact")
    heading = blocks.CharBlock(required=False, max_length=180, default="Let's talk")
    intro = blocks.RichTextBlock(editor="simple", required=False)
    show_email = blocks.BooleanBlock(required=False, default=True)
    show_phone = blocks.BooleanBlock(required=False, default=False)
    show_location = blocks.BooleanBlock(required=False, default=True)
    show_availability = blocks.BooleanBlock(required=False, default=True)
    show_social = blocks.BooleanBlock(required=False, default=True)
    links = blocks.ListBlock(LinkBlock(), required=False, max_num=3, label="Buttons")
    background = blocks.ChoiceBlock(choices=BACKGROUND_CHOICES, default="panel")
    anchor = blocks.CharBlock(required=False, max_length=60, default="contact")
    show_in_page_nav = blocks.BooleanBlock(required=False, default=True)

    class Meta:
        icon = "mail"
        label = "Contact section"
        template = "core/blocks/contact_section.html"


class CTASectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=180)
    text = blocks.RichTextBlock(editor="simple", required=False)
    links = blocks.ListBlock(LinkBlock(), required=False, max_num=3)
    image = ImageChooserBlock(required=False)
    background = blocks.ChoiceBlock(choices=BACKGROUND_CHOICES, default="gradient")
    anchor = blocks.CharBlock(required=False, max_length=60)
    show_in_page_nav = blocks.BooleanBlock(required=False, default=False)

    class Meta:
        icon = "spark"
        label = "Call to action"
        template = "core/blocks/cta_section.html"


class SectionStreamBlock(blocks.StreamBlock):
    section = SectionBlock()
    projects = ProjectsSectionBlock()
    contact = ContactSectionBlock()
    cta = CTASectionBlock()

    class Meta:
        required = False
        block_counts = {}
