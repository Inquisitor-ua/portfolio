import datetime
import json

from django.db import migrations
from django.utils import timezone

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


def taskflow_body(tech):
    return [
        {"type": "heading", "value": {"text": "Overview", "level": "h3", "anchor": ""}},
        {
            "type": "paragraph",
            "value": (
                "<p>Task Flow started as an internal tool for a five-person team that had "
                "outgrown spreadsheets. It grew into a small SaaS product with real-time "
                "boards, per-project reporting, and a permissions model flexible enough for "
                "freelancers and small agencies alike.</p>"
            ),
        },
        {
            "type": "features",
            "value": {
                "items": [
                    {
                        "icon": "check",
                        "title": "Real-time boards",
                        "text": "<p>Drag-and-drop boards that sync instantly across every open session.</p>",
                        "link": EMPTY_LINK,
                    },
                    {
                        "icon": "layers",
                        "title": "Per-project reporting",
                        "text": "<p>Burndown and workload charts generated straight from board activity.</p>",
                        "link": EMPTY_LINK,
                    },
                    {
                        "icon": "briefcase",
                        "title": "Client-friendly access",
                        "text": "<p>Scoped guest accounts so clients only see what's relevant to them.</p>",
                        "link": EMPTY_LINK,
                    },
                ],
                "columns": "3",
            },
        },
        {
            "type": "tech_grid",
            "value": {
                "technologies": [tech["Django"], tech["Vue.js"], tech["PostgreSQL"]],
                "size": "md",
            },
        },
    ]


def devmetrics_body(tech):
    return [
        {"type": "heading", "value": {"text": "Why I built it", "level": "h3", "anchor": ""}},
        {
            "type": "paragraph",
            "value": (
                "<p>Every team I've worked on has asked the same question after an incident: "
                "\"has this gotten better or worse over time?\" DevMetrics answers that by "
                "quietly collecting deployment and incident events and turning them into the "
                "four key DORA metrics.</p>"
            ),
        },
        {
            "type": "code",
            "value": {
                "language": "python",
                "filename": "metrics/deployment_frequency.py",
                "code": (
                    "def deployment_frequency(repo, since):\n"
                    "    deploys = Deployment.objects.filter(\n"
                    "        repo=repo, created_at__gte=since, status=\"success\"\n"
                    "    )\n"
                    "    days = max((timezone.now() - since).days, 1)\n"
                    "    return deploys.count() / days\n"
                ),
            },
        },
        {
            "type": "callout",
            "value": {
                "tone": "info",
                "icon": "spark",
                "title": "Still evolving",
                "text": "<p>DevMetrics is under active development — error budgets and on-call load are next.</p>",
            },
        },
        {
            "type": "tech_grid",
            "value": {
                "technologies": [tech["Django"], tech["Vue.js"], tech["Docker"]],
                "size": "md",
            },
        },
    ]


def create_demo_projects(apps, schema_editor):
    ContentType = apps.get_model("contenttypes.ContentType")
    HomePage = apps.get_model("home.HomePage")
    ProjectIndexPage = apps.get_model("projects.ProjectIndexPage")
    ProjectPage = apps.get_model("projects.ProjectPage")
    Technology = apps.get_model("core.Technology")
    Locale = apps.get_model("wagtailcore.Locale")

    homepage = HomePage.objects.filter(slug="home", depth=2).first()
    if not homepage:
        return

    locale = Locale.objects.first()
    tech = {t.name: t.pk for t in Technology.objects.all()}
    now = timezone.now()

    index_content_type, __ = ContentType.objects.get_or_create(
        model="projectindexpage", app_label="projects"
    )
    project_content_type, __ = ContentType.objects.get_or_create(
        model="projectpage", app_label="projects"
    )

    index_page = ProjectIndexPage.objects.create(
        title="Projects",
        draft_title="Projects",
        slug="projects",
        content_type=index_content_type,
        path="000100010001",
        depth=3,
        numchild=0,
        url_path="/home/projects/",
        locale=locale,
        live=True,
        has_unpublished_changes=False,
        first_published_at=now,
        last_published_at=now,
        latest_revision_created_at=now,
        intro="<p>A selection of things I've designed, built and shipped recently.</p>",
    )

    homepage.numchild = 1
    homepage.save()

    taskflow = ProjectPage.objects.create(
        title="Task Flow",
        draft_title="Task Flow",
        slug="task-flow",
        content_type=project_content_type,
        path="0001000100010001",
        depth=4,
        numchild=0,
        url_path="/home/projects/task-flow/",
        locale=locale,
        live=True,
        has_unpublished_changes=False,
        first_published_at=now,
        last_published_at=now,
        latest_revision_created_at=now,
        summary="A collaborative task and project tracker for small teams, with real-time boards and reporting.",
        subdomain_url="https://taskflow.example.com",
        repo_url="https://github.com/example/taskflow",
        status="live",
        featured=True,
        date_started=datetime.date(2023, 1, 15),
        date_completed=datetime.date(2023, 6, 30),
        body=json.dumps(taskflow_body(tech)),
    )
    taskflow.technologies.set([tech["Django"], tech["Vue.js"], tech["PostgreSQL"]])

    devmetrics = ProjectPage.objects.create(
        title="DevMetrics",
        draft_title="DevMetrics",
        slug="devmetrics",
        content_type=project_content_type,
        path="0001000100010002",
        depth=4,
        numchild=0,
        url_path="/home/projects/devmetrics/",
        locale=locale,
        live=True,
        has_unpublished_changes=False,
        first_published_at=now,
        last_published_at=now,
        latest_revision_created_at=now,
        summary="An analytics dashboard that surfaces deployment frequency, lead time and error budgets for dev teams.",
        subdomain_url="https://devmetrics.example.com",
        repo_url="https://github.com/example/devmetrics",
        status="in_progress",
        featured=True,
        date_started=datetime.date(2024, 2, 1),
        date_completed=None,
        body=json.dumps(devmetrics_body(tech)),
    )
    devmetrics.technologies.set([tech["Django"], tech["Vue.js"], tech["Docker"]])

    index_page.numchild = 2
    index_page.save()


def remove_demo_projects(apps, schema_editor):
    ProjectIndexPage = apps.get_model("projects.ProjectIndexPage")
    ProjectIndexPage.objects.filter(slug="projects", depth=3).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0001_initial"),
        ("home", "0002_create_homepage"),
        ("core", "0002_demo_content"),
    ]

    operations = [
        migrations.RunPython(create_demo_projects, remove_demo_projects),
    ]
