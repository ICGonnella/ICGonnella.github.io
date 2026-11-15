#!/usr/bin/env python3
"""Check generated HTML, local links, structured data and bibliography files."""
import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.references = []
        self.copies = []
        self.h1_count = 0
        self.papers = 0
        self.in_schema = False
        self.schema = ""

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.references.append(attrs[key])
        if tag == "img":
            assert attrs.get("alt"), "Image missing alternative text"
        if tag == "h1":
            self.h1_count += 1
        if tag == "li" and attrs.get("class") == "paper":
            self.papers += 1
        if "data-copy" in attrs:
            self.copies.append(attrs["data-copy"])
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_schema = True

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_schema = False

    def handle_data(self, value):
        if self.in_schema:
            self.schema += value


def check(directory):
    papers = json.loads((ROOT / "data/publications.json").read_text())
    papers.sort(key=lambda paper: paper["date"], reverse=True)
    documents = {}
    for filename in ("index.html", "publications.html", "cv.html"):
        parsed = SiteParser()
        parsed.feed((directory / filename).read_text())
        documents[filename] = parsed
    for filename, parsed in documents.items():
        assert len(parsed.ids) == len(set(parsed.ids)), f"Duplicate HTML IDs in {filename}"
        assert parsed.h1_count == 1, "Expected one page heading"
        assert set(parsed.copies) <= set(parsed.ids), "Missing citation target"
        for reference in parsed.references:
            url = urlparse(reference)
            if url.scheme or url.netloc:
                assert url.scheme in {"https", "mailto"}, f"Unexpected URL: {reference}"
                continue
            if url.path:
                target = directory / unquote(url.path)
                assert target.is_file(), f"Missing local resource: {reference}"
            if url.fragment:
                target_page = unquote(url.path) or filename
                assert unquote(url.fragment) in documents[target_page].ids, f"Missing anchor: {reference}"
        assert json.loads(parsed.schema)["@type"] == "Person"
        expected = papers if filename == "publications.html" else (
            [paper for paper in papers if paper.get("selected")] if filename == "index.html" else []
        )
        assert parsed.papers == len(expected), f"Incorrect paper count in {filename}"
        assert [key for key in parsed.ids if key.startswith("title-")] == ["title-" + paper["id"] for paper in expected], f"Incorrect chronological order in {filename}"
        print(f"PASS: {filename}: {parsed.papers} papers in chronological order, links, IDs and JSON-LD.")
    assert "cv" not in documents["index.html"].ids, "CV must be on its own page"
    assert {"cv", "events"} <= set(documents["cv.html"].ids)
    profile = json.loads((ROOT / "data/profile.json").read_text())
    assert profile["cv_file"] in documents["cv.html"].references, "Missing CV download"
    assert (directory / profile["cv_file"]).read_bytes().startswith(b"%PDF-"), "Invalid CV PDF"
    all_bib = (directory / "files/publications.bib").read_text()
    for paper in papers:
        entry = (directory / f"files/{paper['id']}.bib").read_text()
        assert entry.count("{") == entry.count("}"), f"Unbalanced citation: {paper['id']}"
        assert entry in all_bib, f"Missing combined citation: {paper['id']}"
        assert paper["doi"] in entry, f"Missing DOI: {paper['id']}"
    print("PASS: individual and combined BibTeX files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path, default=ROOT)
    check(parser.parse_args().directory.resolve())
