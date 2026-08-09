import json

from django.db import migrations

TECHNOLOGIES = [
    {"name": "Python", "category": "Backend"},
    {"name": "Django", "category": "Backend"},
    {"name": "PostgreSQL", "category": "Backend"},
    {"name": "Vue.js", "category": "Frontend"},
    {"name": "JavaScript", "category": "Frontend"},
    {"name": "Docker", "category": "Tools"},
]

SOCIAL_LINKS = [
    {"type": "link", "value": {"platform": "github", "url": "https://github.com/example", "label": ""}},
    {"type": "link", "value": {"platform": "linkedin", "url": "https://linkedin.com/in/example", "label": ""}},
    {"type": "link", "value": {"platform": "telegram", "url": "https://t.me/example", "label": ""}},
]

PRIMARY_LINKS = [
    {
        "type": "link",
        "value": {
            "label": label,
            "page": None,
            "external_url": "",
            "document": None,
            "anchor": anchor,
            "style": "ghost",
            "icon": "",
            "open_in_new_tab": False,
        },
    }
    for label, anchor in [
        ("About", "about"),
        ("Experience", "experience"),
        ("Skills", "skills"),
        ("Work", "work"),
        ("Contact", "contact"),
    ]
]


def create_demo_content(apps, schema_editor):
    Site = apps.get_model("wagtailcore.Site")
    Technology = apps.get_model("core.Technology")
    Testimonial = apps.get_model("core.Testimonial")
    SiteBrandingSettings = apps.get_model("core.SiteBrandingSettings")
    NavigationSettings = apps.get_model("core.NavigationSettings")
    ContactSettings = apps.get_model("core.ContactSettings")

    for entry in TECHNOLOGIES:
        Technology.objects.get_or_create(name=entry["name"], defaults={"category": entry["category"]})

    Testimonial.objects.get_or_create(
        name="Priya Anand",
        defaults={
            "role": "Engineering Manager",
            "company": "Nimbus Cloud",
            "quote": (
                "One of the most reliable engineers I've worked with — they turned a "
                "vague brief into a polished, well-tested feature in days, not weeks."
            ),
        },
    )

    site = Site.objects.get(is_default_site=True)

    SiteBrandingSettings.objects.get_or_create(
        site=site,
        defaults={
            "site_name": "Alex Morgan",
            "tagline": "Full-Stack Developer building fast, accessible web apps.",
        },
    )

    NavigationSettings.objects.get_or_create(
        site=site,
        defaults={
            "primary_links": json.dumps(PRIMARY_LINKS),
            "footer_note": "Built with Django, Wagtail & Vue.",
        },
    )

    ContactSettings.objects.get_or_create(
        site=site,
        defaults={
            "email": "hello@example.com",
            "phone": "",
            "location": "Remote / Europe",
            "availability_available": True,
            "availability_text": "Available for new opportunities",
            "social_links": json.dumps(SOCIAL_LINKS),
        },
    )


def remove_demo_content(apps, schema_editor):
    # Intentionally left as a no-op: settings/snippets are safe to keep even
    # if this migration is reversed, and may already have been edited.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
        ("wagtailcore", "0002_initial_data"),
    ]

    operations = [
        migrations.RunPython(create_demo_content, remove_demo_content),
    ]
