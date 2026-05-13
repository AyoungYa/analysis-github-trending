#!/usr/bin/env python3
"""Fetch and parse GitHub Trending repositories.

This script intentionally uses only the Python standard library so it can be
bundled inside agent skills without dependency installation.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import html
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable


GITHUB_TRENDING_URL = "https://github.com/trending"
VALID_SINCE = {"daily", "weekly", "monthly"}
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; gh-trend/0.1; "
    "+https://github.com/trending)"
)


@dataclasses.dataclass
class TrendingRepo:
    rank: int
    owner: str
    name: str
    full_name: str
    url: str
    description: str | None
    language: str | None
    language_color: str | None
    stars: int | None
    forks: int | None
    stars_period: int | None
    period_label: str | None
    since: str
    fetched_at: str
    source_url: str


def build_trending_url(
    language: str | None,
    since: str,
    spoken_language_code: str | None = None,
) -> str:
    if since not in VALID_SINCE:
        raise ValueError(f"invalid since={since!r}; expected one of {sorted(VALID_SINCE)}")

    base = GITHUB_TRENDING_URL
    if language:
        base = f"{base}/{urllib.parse.quote(language.strip('/'))}"

    query = {"since": since}
    if spoken_language_code:
        query["spoken_language_code"] = spoken_language_code
    return f"{base}?{urllib.parse.urlencode(query)}"


def fetch_html(url: str, timeout: float, user_agent: str, insecure: bool = False) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    context = ssl._create_unverified_context() if insecure else None
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def parse_trending_html(raw_html: str, since: str, source_url: str) -> list[TrendingRepo]:
    articles = re.findall(r"<article\b.*?</article>", raw_html, flags=re.IGNORECASE | re.DOTALL)
    fetched_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    repos: list[TrendingRepo] = []

    for article in articles:
        full_name = _extract_full_name(article)
        if not full_name:
            continue

        owner, name = full_name.split("/", 1)
        repos.append(
            TrendingRepo(
                rank=len(repos) + 1,
                owner=owner,
                name=name,
                full_name=full_name,
                url=f"https://github.com/{full_name}",
                description=_extract_description(article),
                language=_extract_language(article),
                language_color=_extract_language_color(article),
                stars=_extract_repo_link_count(article, full_name, "stargazers"),
                forks=_extract_repo_link_count(article, full_name, "forks"),
                stars_period=_extract_period_stars(article),
                period_label=_extract_period_label(article),
                since=since,
                fetched_at=fetched_at,
                source_url=source_url,
            )
        )

    return repos


def repos_to_json(repos: Iterable[TrendingRepo]) -> str:
    return json.dumps(
        [dataclasses.asdict(repo) for repo in repos],
        ensure_ascii=False,
        indent=2,
    )


def repos_to_markdown(repos: list[TrendingRepo]) -> str:
    lines = [
        "# GitHub Trending Repositories",
        "",
        "| # | Repository | Language | Stars | Forks | Period stars | Description |",
        "| ---: | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for repo in repos:
        lines.append(
            "| {rank} | [{full_name}]({url}) | {language} | {stars} | {forks} | "
            "{stars_period} | {description} |".format(
                rank=repo.rank,
                full_name=_escape_markdown_cell(repo.full_name),
                url=repo.url,
                language=_escape_markdown_cell(repo.language or ""),
                stars=_format_optional_int(repo.stars),
                forks=_format_optional_int(repo.forks),
                stars_period=_format_optional_int(repo.stars_period),
                description=_escape_markdown_cell(repo.description or ""),
            )
        )
    return "\n".join(lines) + "\n"


def write_output(content: str, output: Path | None) -> None:
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
    else:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")


def _extract_full_name(article: str) -> str | None:
    h2_match = re.search(r"<h2\b.*?</h2>", article, flags=re.IGNORECASE | re.DOTALL)
    if not h2_match:
        return None
    href_match = re.search(r'href="(/[^"/\s]+/[^"#?\s]+)"', h2_match.group(0))
    if not href_match:
        return None
    return href_match.group(1).strip("/").replace(" ", "")


def _extract_description(article: str) -> str | None:
    match = re.search(r"<p\b[^>]*>(.*?)</p>", article, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    value = _strip_tags(match.group(1))
    return value or None


def _extract_language(article: str) -> str | None:
    match = re.search(
        r'itemprop="programmingLanguage"[^>]*>(.*?)</span>',
        article,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None
    value = _strip_tags(match.group(1))
    return value or None


def _extract_language_color(article: str) -> str | None:
    match = re.search(
        r'repo-language-color[^>]*style="[^"]*background-color:\s*([^;"\s]+)',
        article,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return html.unescape(match.group(1)) if match else None


def _extract_repo_link_count(article: str, full_name: str, suffix: str) -> int | None:
    pattern = (
        r'<a\b[^>]*href="/'
        + re.escape(full_name)
        + r"/"
        + re.escape(suffix)
        + r'"[^>]*>(.*?)</a>'
    )
    match = re.search(pattern, article, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return _parse_int(_strip_tags(match.group(1)))


def _extract_period_stars(article: str) -> int | None:
    text = _strip_tags(article)
    match = re.search(
        r"([\d,]+)\s+stars?\s+(today|this week|this month)",
        text,
        flags=re.IGNORECASE,
    )
    return _parse_int(match.group(1)) if match else None


def _extract_period_label(article: str) -> str | None:
    text = _strip_tags(article)
    match = re.search(
        r"[\d,]+\s+stars?\s+(today|this week|this month)",
        text,
        flags=re.IGNORECASE,
    )
    return match.group(1).lower() if match else None


def _strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _parse_int(value: str) -> int | None:
    match = re.search(r"[\d,]+", value)
    if not match:
        return None
    return int(match.group(0).replace(",", ""))


def _format_optional_int(value: int | None) -> str:
    return "" if value is None else f"{value:,}"


def _escape_markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch GitHub Trending repositories as JSON or Markdown.",
    )
    parser.add_argument(
        "-l",
        "--language",
        help="GitHub Trending language slug, for example python, typescript, rust.",
    )
    parser.add_argument(
        "-s",
        "--since",
        choices=sorted(VALID_SINCE),
        default="daily",
        help="Trending time range.",
    )
    parser.add_argument(
        "--spoken-language-code",
        help="GitHub spoken language code filter, for example zh or en.",
    )
    parser.add_argument(
        "--url",
        help="Custom trending URL. Overrides --language, --since, and --spoken-language-code for fetching.",
    )
    parser.add_argument(
        "--input-html",
        type=Path,
        help="Parse a local GitHub Trending HTML file instead of fetching from the network.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of repositories to output.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write output to a file instead of stdout.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="Network timeout in seconds.",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="HTTP User-Agent used when fetching GitHub.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification. Use only when local Python certificates are broken.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_url = args.url or build_trending_url(
        args.language,
        args.since,
        args.spoken_language_code,
    )

    try:
        if args.input_html:
            raw_html = args.input_html.read_text(encoding="utf-8")
            source_url = str(args.input_html)
        else:
            raw_html = fetch_html(source_url, args.timeout, args.user_agent, args.insecure)

        repos = parse_trending_html(raw_html, args.since, source_url)
        if args.limit is not None:
            repos = repos[: max(args.limit, 0)]

        if not repos:
            raise RuntimeError(
                "no repositories parsed; GitHub Trending markup may have changed "
                "or the input HTML is not a trending page"
            )

        content = repos_to_json(repos) if args.format == "json" else repos_to_markdown(repos)
        write_output(content, args.output)
        return 0
    except Exception as exc:
        print(f"fetch_trending.py: error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
