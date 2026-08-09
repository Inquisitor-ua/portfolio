import json

from django.db import migrations
from django.utils import timezone

HERO_BUTTONS = [
    {
        "type": "button",
        "value": {
            "label": "View projects",
            "page": None,
            "external_url": "",
            "document": None,
            "anchor": "work",
            "style": "primary",
            "icon": "arrow-down",
            "open_in_new_tab": False,
        },
    },
    {
        "type": "button",
        "value": {
            "label": "Get in touch",
            "page": None,
            "external_url": "",
            "document": None,
            "anchor": "contact",
            "style": "secondary",
            "icon": "mail",
            "open_in_new_tab": False,
        },
    },
]

ABOUT_PARAGRAPH = (
    "<p>I'm a full-stack developer who enjoys taking a product from a rough idea to a "
    "polished, production-ready release. My day-to-day toolkit is Django and Wagtail on "
    "the backend, Vue on the front end, and Docker to ship it all reliably.</p>"
    "<p>Outside of client work, I like distilling messy processes into small, "
    "well-tested tools — this site is one of them.</p>"
)

EMPTY_LINK = {
    "label": "",
    "page": None,
    "external_url": "",
    "document": None,
    "anchor": "",
    "style": "primary",
    "icon": "",
    "open_in_new_tab": False,
}


def build_body(tech, testimonial_id):
    return [
        {
            "type": "section",
            "value": {
                "eyebrow": "About",
                "heading": "About me",
                "intro": "",
                "content": [
                    {"type": "paragraph", "value": ABOUT_PARAGRAPH},
                    {
                        "type": "stats",
                        "value": {
                            "items": [
                                {"value": "5", "suffix": "+", "label": "Years of experience"},
                                {"value": "30", "suffix": "+", "label": "Projects shipped"},
                                {"value": "8", "suffix": "", "label": "Technologies mastered"},
                            ],
                            "animate": True,
                        },
                    },
                ],
                "width": "normal",
                "align": "start",
                "background": "none",
                "anchor": "about",
                "show_in_page_nav": True,
            },
        },
        {
            "type": "section",
            "value": {
                "eyebrow": "Experience",
                "heading": "Where I've worked",
                "intro": "",
                "content": [
                    {
                        "type": "timeline",
                        "value": {
                            "entries": [
                                {
                                    "period": "2022 — present",
                                    "title": "Senior Full-Stack Developer",
                                    "organisation": "Nimbus Cloud",
                                    "organisation_url": "",
                                    "location": "Remote",
                                    "description": (
                                        "<p>Leading development of the customer-facing "
                                        "dashboard and the internal admin tooling built on "
                                        "Django and Wagtail.</p>"
                                    ),
                                    "technologies": [tech["Django"], tech["Vue.js"], tech["PostgreSQL"]],
                                    "current": True,
                                },
                                {
                                    "period": "2019 — 2022",
                                    "title": "Full-Stack Developer",
                                    "organisation": "Brightloop Studio",
                                    "organisation_url": "",
                                    "location": "Berlin, Germany",
                                    "description": (
                                        "<p>Built and maintained several client web "
                                        "applications, from marketing sites to small SaaS "
                                        "products.</p>"
                                    ),
                                    "technologies": [tech["Python"], tech["Django"], tech["JavaScript"]],
                                    "current": False,
                                },
                            ],
                            "icon": "briefcase",
                        },
                    }
                ],
                "width": "normal",
                "align": "start",
                "background": "tint",
                "anchor": "experience",
                "show_in_page_nav": True,
            },
        },
        {
            "type": "section",
            "value": {
                "eyebrow": "Skills",
                "heading": "What I work with",
                "intro": "",
                "content": [
                    {
                        "type": "skills",
                        "value": {
                            "groups": [
                                {
                                    "name": "Backend",
                                    "skills": [
                                        {"name": "Python", "level": 5, "note": ""},
                                        {"name": "Django", "level": 5, "note": ""},
                                        {"name": "PostgreSQL", "level": 4, "note": ""},
                                    ],
                                },
                                {
                                    "name": "Frontend",
                                    "skills": [
                                        {"name": "Vue.js", "level": 4, "note": ""},
                                        {"name": "JavaScript", "level": 4, "note": ""},
                                        {"name": "CSS", "level": 4, "note": ""},
                                    ],
                                },
                                {
                                    "name": "Tools",
                                    "skills": [
                                        {"name": "Docker", "level": 4, "note": ""},
                                        {"name": "Git", "level": 5, "note": ""},
                                    ],
                                },
                            ],
                            "show_levels": True,
                        },
                    },
                    {
                        "type": "tech_grid",
                        "value": {
                            "technologies": [
                                tech["Python"],
                                tech["Django"],
                                tech["PostgreSQL"],
                                tech["Vue.js"],
                                tech["JavaScript"],
                                tech["Docker"],
                            ],
                            "size": "md",
                        },
                    },
                ],
                "width": "normal",
                "align": "start",
                "background": "none",
                "anchor": "skills",
                "show_in_page_nav": True,
            },
        },
        {
            "type": "projects",
            "value": {
                "eyebrow": "Work",
                "heading": "Selected projects",
                "intro": "",
                "source": "featured",
                "projects": [],
                "limit": 6,
                "layout": "grid",
                "show_filters": True,
                "cta": EMPTY_LINK,
                "background": "none",
                "anchor": "work",
                "show_in_page_nav": True,
            },
        },
        {
            "type": "section",
            "value": {
                "eyebrow": "Feedback",
                "heading": "What people say",
                "intro": "",
                "content": [
                    {
                        "type": "testimonials",
                        "value": {"testimonials": [testimonial_id], "columns": "1"},
                    }
                ],
                "width": "normal",
                "align": "center",
                "background": "panel",
                "anchor": "testimonials",
                "show_in_page_nav": False,
            },
        },
        {
            "type": "contact",
            "value": {
                "eyebrow": "Contact",
                "heading": "Let's build something",
                "intro": "<p>Have a project in mind or just want to say hello? My inbox is open.</p>",
                "show_email": True,
                "show_phone": False,
                "show_location": True,
                "show_availability": True,
                "show_social": True,
                "links": [],
                "background": "panel",
                "anchor": "contact",
                "show_in_page_nav": True,
            },
        },
    ]


def create_homepage(apps, schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")
    Page = apps.get_model("wagtailcore.Page")
    Site = apps.get_model("wagtailcore.Site")
    Locale = apps.get_model("wagtailcore.Locale")
    HomePage = apps.get_model("home.HomePage")
    Technology = apps.get_model("core.Technology")
    Testimonial = apps.get_model("core.Testimonial")

    page_content_type = ContentType.objects.get(model="page", app_label="wagtailcore")
    root_page = Page.objects.get(depth=1)

    # Point the default site at the root page first, otherwise deleting the
    # placeholder homepage below would cascade-delete the Site too.
    site = Site.objects.get(is_default_site=True)
    site.root_page = root_page
    site.save()

    Page.objects.filter(content_type=page_content_type, slug="home", depth=2).delete()

    homepage_content_type, __ = ContentType.objects.get_or_create(
        model="homepage", app_label="home"
    )

    locale = Locale.objects.first()
    tech = {t.name: t.pk for t in Technology.objects.all()}
    testimonial = Testimonial.objects.first()
    now = timezone.now()

    homepage = HomePage.objects.create(
        title="Alex Morgan",
        draft_title="Alex Morgan",
        slug="home",
        content_type=homepage_content_type,
        path="00010001",
        depth=2,
        numchild=0,
        url_path="/home/",
        locale=locale,
        live=True,
        has_unpublished_changes=False,
        first_published_at=now,
        last_published_at=now,
        latest_revision_created_at=now,
        role="Full-Stack Developer",
        intro=(
            "<p>I build fast, accessible web applications end-to-end — from Django/Wagtail "
            "backends to polished Vue front-ends. Currently focused on developer tooling and "
            "clean, maintainable architecture.</p>"
        ),
        hero_buttons=json.dumps(HERO_BUTTONS),
        body=json.dumps(build_body(tech, testimonial.pk if testimonial else None)),
    )

    site.root_page = homepage
    site.save()


def remove_homepage(apps, schema_editor):
    HomePage = apps.get_model("home.HomePage")
    HomePage.objects.filter(slug="home", depth=2).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0001_initial"),
        ("core", "0002_demo_content"),
    ]

    operations = [
        migrations.RunPython(create_homepage, remove_homepage),
    ]
