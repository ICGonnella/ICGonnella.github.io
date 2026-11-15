#!/usr/bin/env python3
"""Generate the static site using only the Python standard library."""
import argparse
import json
import re
import shutil
from html import escape
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]


def text(value):
    return escape(str(value), quote=True)


def bibtex(paper):
    kind = "misc" if paper["type"] == "preprint" else paper["type"]
    fields = {
        "title": "{" + paper["title"] + "}",
        "author": " and ".join(paper["authors"]),
        "year": str(paper["year"]),
    }
    if kind == "article":
        fields["journal"] = paper["venue"]
    elif kind == "incollection":
        fields["booktitle"] = paper["venue"]
    for key in ("volume", "number", "pages", "series", "publisher", "doi"):
        if paper.get(key):
            fields[key] = paper[key]
    if paper.get("arxiv"):
        fields.update(eprint=paper["arxiv"], archivePrefix="arXiv", primaryClass="math.NA")
    def tex_value(key, value):
        if key in {"title", "author", "journal", "booktitle", "series", "publisher"}:
            return re.sub(r"([&%#$_])", r"\\\1", value)
        return value

    return f"@{kind}{{{paper['id']},\n" + ",\n".join(
        f"  {key} = {{{tex_value(key, value)}}}" for key, value in fields.items()
    ) + "\n}\n"


def render_paper(paper, name):
    authors = ", ".join(
        f"<strong>{text(author)}</strong>" if author == name else text(author)
        for author in paper["authors"]
    )
    doi_url = f"https://doi.org/{paper['doi']}"
    venue = f"{paper['year']} · {paper['venue']}"
    if paper["type"] == "preprint":
        venue = f"{paper['year']} · Preprint · {paper['venue']}"
    elif paper["type"] == "incollection":
        venue += " · Book chapter"
    links = ""
    if paper["type"] != "preprint":
        links = f'<a href="{text(doi_url)}">DOI<span class="visually-hidden"> for {text(paper["title"])}</span></a>'
    if paper.get("arxiv"):
        links += f'<a href="https://arxiv.org/abs/{text(paper["arxiv"])}">arXiv</a>'
    key = text(paper["id"])
    citation = text(bibtex(paper))
    return f'''<li class="paper">
      <article aria-labelledby="title-{key}">
        <h3 id="title-{key}"><a href="{text(doi_url)}">{text(paper['title'])}</a></h3>
        <p class="paper-authors">{authors}</p>
        <div class="paper-meta">
          <p class="paper-venue">{text(venue)}</p>
          <div class="paper-actions">{links}
          <details class="citation"><summary>BibTeX<span class="visually-hidden"> for {text(paper['title'])}</span></summary>
            <div class="citation-panel"><pre><code id="bib-{key}">{citation}</code></pre>
              <div class="citation-tools"><button type="button" class="copy-citation" data-copy="bib-{key}" hidden>Copy citation</button><a href="files/{key}.bib" download>Download .bib</a></div>
            </div>
          </details>
          </div>
        </div>
      </article>
    </li>'''


def render_timeline(entries):
    rendered = []
    for entry in entries:
        title = text(entry["title"])
        if entry.get("url"):
            title = f'<a href="{text(entry["url"])}">{title}</a>'
        rendered.append(f'<li><span class="timeline-date">{text(entry["date"])}</span>'
                        f'<div><h4>{title}</h4><p>{text(entry["detail"])}</p></div></li>')
    return "\n".join(rendered)


def build(destination):
    profile = json.loads((ROOT / "data/profile.json").read_text())
    papers = json.loads((ROOT / "data/publications.json").read_text())
    ids = [paper["id"] for paper in papers]
    if len(set(ids)) != len(ids) or not all(re.fullmatch(r"[a-z0-9-]+", key) for key in ids):
        raise ValueError("Publication IDs must be unique lowercase letters, digits or hyphens.")
    for paper in papers:
        if paper["type"] not in {"preprint", "article", "incollection"}:
            raise ValueError(f"Unsupported publication type: {paper['type']}")
    papers.sort(key=lambda paper: paper["date"], reverse=True)
    destination.mkdir(parents=True, exist_ok=True)
    files = destination / "files"
    files.mkdir(exist_ok=True)
    for paper in papers:
        (files / f"{paper['id']}.bib").write_text(bibtex(paper), encoding="utf-8")
    (files / "publications.bib").write_text("\n".join(map(bibtex, papers)), encoding="utf-8")
    values = {key: text(value) for key, value in profile.items() if isinstance(value, str)}
    values["about"] = "\n".join(f"<p>{text(paragraph)}</p>" for paragraph in profile["about"])
    values["selected_papers"] = "\n".join(render_paper(paper, profile["name"]) for paper in papers if paper.get("selected"))
    values["all_papers"] = "\n".join(render_paper(paper, profile["name"]) for paper in papers)
    for group in ("education", "activities", "talks", "awards"):
        values[group] = render_timeline(profile[group])
    values["address"] = "<br>".join(map(text, profile["address"]))
    values["upcoming_events"] = "\n".join(
        f'<article class="event-announcement">'
        f'<h3>{text(event["title"])}</h3>'
        f'<p class="event-status">Co-organizer · More details coming soon</p></article>'
        for event in profile.get("upcoming_events", [])
    )
    values["cv_link"] = ""
    if profile.get("cv_file"):
        cv = ROOT / profile["cv_file"]
        if not cv.is_file():
            raise FileNotFoundError(f"CV file not found: {cv}")
        values["cv_link"] = (
            f'<a class="cv-download-link" href="{text(profile["cv_file"])}" '
            'download="Isabella-Carla-Gonnella-CV.pdf">Download CV (PDF) '
            '<span aria-hidden="true">↓</span></a>'
        )
        if destination != ROOT:
            target = destination / profile["cv_file"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(cv, target)
    values["structured_data"] = json.dumps({
        "@context": "https://schema.org", "@type": "Person", "name": profile["name"],
        "url": profile["url"], "jobTitle": profile["role"], "description": profile["description"],
        "affiliation": {"@type": "Organization", "name": "SISSA"},
        "image": profile["url"] + profile["portrait"],
        "sameAs": [profile["scholar"], profile["linkedin"]]
    }, ensure_ascii=False).replace("<", "\\u003c")
    source = Template((ROOT / "templates/index.html").read_text())
    pages = (
        ("index.html", "home.html", "Numerical Analysis & Machine Learning", "#about"),
        ("publications.html", "publications.html", "Publications & preprints", "#publications"),
        ("cv.html", "cv.html", "CV & Info", "#cv"),
    )
    for filename, content_template, title, top_anchor in pages:
        is_home = filename == "index.html"
        home = "" if is_home else "index.html"
        about_current = ' aria-current="location"' if is_home else ""
        publications_current = ' aria-current="page"' if filename == "publications.html" else ""
        cv_current = ' aria-current="page"' if filename == "cv.html" else ""
        values["navigation"] = (
            f'<a href="{home}#about"{about_current}>About &amp; Research</a>\n'
            f'<a href="publications.html"{publications_current}>Publications &amp; Preprints</a>\n'
            f'<a href="cv.html"{cv_current}>CV &amp; Info</a>'
        )
        values["page_title"] = text(
            f"{profile['name']} | Numerical Analysis & Machine Learning" if is_home
            else f"{title} | {profile['name']}"
        )
        values["page_url"] = text(profile["url"] + ("" if is_home else filename))
        values["top_anchor"] = top_anchor
        values["main_content"] = Template((ROOT / "templates" / content_template).read_text()).substitute(values)
        (destination / filename).write_text(source.substitute(values), encoding="utf-8")
    (destination / ".nojekyll").touch()
    (destination / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {profile['url']}sitemap.xml\n")
    (destination / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'<url><loc>{text(profile["url"])}</loc></url>'
        f'<url><loc>{text(profile["url"])}publications.html</loc></url>'
        f'<url><loc>{text(profile["url"])}cv.html</loc></url></urlset>\n')
    if destination != ROOT:
        shutil.copytree(ROOT / "assets", destination / "assets", dirs_exist_ok=True)
        portrait = destination / profile["portrait"]
        portrait.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / profile["portrait"], portrait)
    print(f"Built home, publications and CV pages in {destination} ({len(papers)} publications)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT, help="Output directory (default: repository root)")
    args = parser.parse_args()
    build(args.output.resolve())
