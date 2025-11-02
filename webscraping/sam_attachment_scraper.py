#!/usr/bin/env python3
"""Download SAM.gov opportunity attachments listed in the filtered SQLite DB.

Usage example:

python webscraping/sam_attachment_scraper.py \
    --keyword "security guard" \
    --tables fy2025_archived_opportunities \
    --pages 1 \
    --output-dir webscraping/downloads

The script will open each opportunity link in Playwright, navigate to the
"Attachments/Links" tab, click "Download All", and store the resulting ZIP file
under the chosen output directory. Results are throttled with small random
sleeps to mimic manual browsing.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import logging
import random
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

from playwright.async_api import Browser, Page, TimeoutError as PlaywrightTimeoutError, async_playwright

LOGGER = logging.getLogger("sam_attachment_scraper")
DEFAULT_DB_PATH = Path("db/sam_archived_opportunities_filtered.sqlite")
DEFAULT_TABLE = "fy2025_archived_opportunities"
INVALID_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
MAX_FILENAME_LENGTH = 180
MAX_PATH_LENGTH = 255
DOWNLOAD_PATH_COLUMN = "DownloadPath"


@dataclass
class Opportunity:
    notice_id: str
    title: str
    link: str
    table: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download SAM.gov attachments using links from the archived opportunities DB.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="Path to sam_archived_opportunities_filtered.sqlite",
    )
    parser.add_argument(
        "--tables",
        nargs="*",
        default=[DEFAULT_TABLE],
        help="One or more tables to scan for links (ordered priority).",
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default=None,
        help="Optional case-insensitive substring to match in the Title column.",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="How many 25-result pages to process (page size is configurable).",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=25,
        help="How many opportunities constitute a page (mirrors the search UI).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("webscraping/downloads"),
        help="Where to store the downloaded ZIP bundles.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Chromium in headless mode (recommended for automation).",
    )
    parser.add_argument(
        "--nav-timeout",
        type=int,
        default=45,
        help="Navigation timeout in seconds for each opportunity page.",
    )
    parser.add_argument(
        "--download-timeout",
        type=int,
        default=60,
        help="Timeout in seconds while waiting for the ZIP to finish downloading.",
    )
    parser.add_argument(
        "--throttle-min",
        type=float,
        default=2.5,
        help="Minimum seconds to wait between opportunities.",
    )
    parser.add_argument(
        "--throttle-max",
        type=float,
        default=5.5,
        help="Maximum seconds to wait between opportunities.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    args = parser.parse_args()

    if args.pages < 1:
        parser.error("--pages must be >= 1")
    if args.page_size < 1:
        parser.error("--page-size must be >= 1")
    if args.throttle_min < 0 or args.throttle_max < 0 or args.throttle_min > args.throttle_max:
        parser.error("Throttle values must be non-negative and min <= max")
    return args


def sanitize_filename(name: str) -> str:
    """Replace characters that are not filesystem friendly."""
    return INVALID_FILENAME_CHARS.sub("_", name.strip()) or "attachment"


def ensure_download_column(conn: sqlite3.Connection, table: str) -> None:
    """Ensure the destination table has a column for storing download paths."""
    cursor = conn.execute(f'PRAGMA table_info("{table}")')
    columns = {row[1] for row in cursor.fetchall()}
    if DOWNLOAD_PATH_COLUMN not in columns:
        conn.execute(f'ALTER TABLE "{table}" ADD COLUMN "{DOWNLOAD_PATH_COLUMN}" TEXT')
        conn.commit()


def truncate_filename(filename: str, max_length: int = MAX_FILENAME_LENGTH) -> str:
    """Truncate overly long filenames while retaining uniqueness with a hash suffix."""
    if len(filename) <= max_length:
        return filename

    stem = Path(filename).stem
    ext = Path(filename).suffix
    if not ext:
        ext = ".zip"

    digest = hashlib.sha1(filename.encode("utf-8", "ignore")).hexdigest()[:8]
    allowance = max_length - len(ext) - len(digest) - 1  # account for _ between stem and hash
    if allowance < 1:
        allowance = max_length - len(ext)
        truncated = stem[:allowance]
        return f"{truncated}{ext}"

    truncated = stem[:allowance]
    if not truncated:
        truncated = digest
        return f"{truncated}{ext}"

    return f"{truncated}_{digest}{ext}"


def build_output_path(destination_dir: Path, opportunity: Opportunity, suggested_name: str | None) -> Path:
    """Create a filesystem-safe, length-limited output path for a download."""
    suggested = sanitize_filename(suggested_name or "download.zip")
    if not suggested.lower().endswith(".zip"):
        suggested = f"{suggested}.zip"

    notice_component = sanitize_filename(opportunity.notice_id)
    combined = f"{notice_component}_{suggested}"
    combined = truncate_filename(combined)

    output_path = destination_dir / combined
    if len(str(output_path)) <= MAX_PATH_LENGTH:
        return output_path

    overflow = len(str(output_path)) - MAX_PATH_LENGTH
    max_filename_length = max(1, len(combined) - overflow)
    adjusted = truncate_filename(combined, max_filename_length)
    final_path = destination_dir / adjusted
    if len(str(final_path)) > MAX_PATH_LENGTH:
        # As a last resort, fall back to a strictly hashed filename.
        digest = hashlib.sha1(str(final_path).encode("utf-8", "ignore")).hexdigest()[:16]
        final_path = destination_dir / f"{notice_component}_{digest}.zip"
    return final_path


def record_download_path(conn: sqlite3.Connection, opportunity: Opportunity, download_path: Path) -> None:
    """Store the relative download path for an opportunity in the database."""
    relative_path = download_path.as_posix()
    cursor = conn.execute(
        f'UPDATE "{opportunity.table}" SET "{DOWNLOAD_PATH_COLUMN}" = ? WHERE NoticeId = ?',
        (relative_path, opportunity.notice_id),
    )
    if cursor.rowcount:
        conn.commit()
    else:
        LOGGER.debug("No row updated for %s in %s", opportunity.notice_id, opportunity.table)


def fetch_opportunities(
    db_path: Path,
    tables: Sequence[str],
    keyword: str | None,
    limit: int,
) -> List[Opportunity]:
    if not db_path.exists():
        raise FileNotFoundError(db_path)

    keyword_like = f"%{keyword.lower()}%" if keyword else None

    conn = sqlite3.connect(str(db_path))
    conn.text_factory = lambda b: b.decode("utf-8", "replace") if isinstance(b, bytes) else str(b)
    conn.row_factory = sqlite3.Row
    opportunities: List[Opportunity] = []

    try:
        for table in tables:
            remaining = limit - len(opportunities)
            if remaining <= 0:
                break
            ensure_download_column(conn, table)
            sql = f"SELECT NoticeId, Title, Link FROM {table} WHERE Link IS NOT NULL AND Link != ''"
            params: List[object] = []
            if keyword_like:
                sql += " AND lower(Title) LIKE ?"
                params.append(keyword_like)
            sql += " ORDER BY rowid DESC LIMIT ?"
            params.append(remaining)

            LOGGER.debug("Querying %s (remaining=%s)", table, remaining)
            for row in conn.execute(sql, params):
                opportunities.append(
                    Opportunity(
                        notice_id=row["NoticeId"],
                        title=row["Title"],
                        link=row["Link"],
                        table=table,
                    )
                )
    finally:
        conn.close()

    return opportunities


async def ensure_attachments_tab(page: Page) -> None:
    """Switch to the Attachments/Links tab if present."""
    try:
        tab = page.get_by_role("link", name="Attachments/Links")
        await tab.wait_for(state="visible", timeout=5000)
        await tab.click()
        await page.wait_for_timeout(500)  # allow content to swap
    except PlaywrightTimeoutError:
        LOGGER.debug("Attachments tab not found on %s", page.url)


async def download_bundle(
    page: Page,
    opportunity: Opportunity,
    destination_dir: Path,
    nav_timeout: int,
    download_timeout: int,
) -> Path | None:
    try:
        await page.goto(opportunity.link, wait_until="networkidle", timeout=nav_timeout * 1000)
    except PlaywrightTimeoutError:
        LOGGER.warning("Navigation timed out for %s", opportunity.link)
        return None

    # Allow the layout to settle before we search for the attachments panel.
    await page.wait_for_timeout(2000)
    await ensure_attachments_tab(page)

    download_button = page.get_by_role("button", name=re.compile("Download All", re.IGNORECASE))
    try:
        await download_button.wait_for(state="visible", timeout=5000)
    except PlaywrightTimeoutError:
        LOGGER.info("No 'Download All' button for %s", opportunity.notice_id)
        return None

    try:
        async with page.expect_download(timeout=download_timeout * 1000) as download_info:
            await download_button.click()
        download = await download_info.value
        LOGGER.debug("Download URL for %s: %s", opportunity.notice_id, download.url)
    except PlaywrightTimeoutError:
        LOGGER.warning("Download timed out for %s", opportunity.notice_id)
        return None

    output_path = build_output_path(destination_dir, opportunity, download.suggested_filename)
    try:
        await download.save_as(output_path)
    except OSError as exc:  # pragma: no cover - safety net for unforeseen filesystem issues
        LOGGER.error("Failed to save download for %s: %s", opportunity.notice_id, exc)
        return None
    LOGGER.info("Saved %s (%s)", output_path, opportunity.title)
    return output_path


async def process_opportunities(args: argparse.Namespace, opportunities: Sequence[Opportunity]) -> None:
    args.output_dir.mkdir(parents=True, exist_ok=True)

    db_conn = sqlite3.connect(str(args.db))
    db_conn.text_factory = lambda b: b.decode("utf-8", "replace") if isinstance(b, bytes) else str(b)

    for table in sorted({op.table for op in opportunities}):
        ensure_download_column(db_conn, table)

    async with async_playwright() as playwright:
        browser: Browser = await playwright.chromium.launch(headless=args.headless)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        successes = 0
        for idx, opportunity in enumerate(opportunities, start=1):
            LOGGER.info("[%s/%s] Processing %s (%s)", idx, len(opportunities), opportunity.notice_id, opportunity.table)
            downloaded = await download_bundle(
                page,
                opportunity,
                args.output_dir,
                args.nav_timeout,
                args.download_timeout,
            )
            if downloaded:
                successes += 1
                record_download_path(db_conn, opportunity, downloaded)

            sleep_for = random.uniform(args.throttle_min, args.throttle_max)
            await asyncio.sleep(sleep_for)

        LOGGER.info("Finished: %s/%s downloads succeeded", successes, len(opportunities))
        await context.close()
        await browser.close()
    db_conn.close()


async def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    limit = args.pages * args.page_size
    LOGGER.info(
        "Querying up to %s opportunities from %s (tables=%s, keyword=%s)",
        limit,
        args.db,
        ",".join(args.tables),
        args.keyword or "<any>",
    )

    opportunities = fetch_opportunities(args.db, args.tables, args.keyword, limit)
    if not opportunities:
        LOGGER.warning("No opportunities matched the filters")
        return

    LOGGER.info("Found %s opportunities to process", len(opportunities))
    await process_opportunities(args, opportunities)


if __name__ == "__main__":
    asyncio.run(main())
