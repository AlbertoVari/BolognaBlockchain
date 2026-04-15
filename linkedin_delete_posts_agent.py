#!/usr/bin/env python3
"""
LinkedIn Post Cleanup Agent

Automates deletion of posts from your own LinkedIn profile activity page.
Use at your own risk; UI selectors may change over time.
"""

import argparse
import asyncio
import os
import sys
from typing import Optional

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

LINKEDIN_POSTS_URL = "https://www.linkedin.com/in/me/recent-activity/all/"


async def human_pause(seconds: float = 0.8) -> None:
    await asyncio.sleep(seconds)


async def ensure_logged_in(page, li_at_cookie: Optional[str]) -> None:
    if li_at_cookie:
        context = page.context
        await context.add_cookies(
            [
                {
                    "name": "li_at",
                    "value": li_at_cookie,
                    "domain": ".linkedin.com",
                    "path": "/",
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "Lax",
                }
            ]
        )

    await page.goto(LINKEDIN_POSTS_URL, wait_until="domcontentloaded")
    await human_pause(1.2)

    if "login" in page.url.lower() or "checkpoint" in page.url.lower():
        raise RuntimeError(
            "Not logged in. Provide LI_AT cookie via --li-at or LI_AT env variable, "
            "or sign in manually and rerun with --headed."
        )


async def scroll_feed(page, times: int = 2) -> None:
    for _ in range(times):
        await page.mouse.wheel(0, 2500)
        await human_pause(1.0)


async def open_post_menu(post) -> bool:
    menu_selectors = [
        "button[aria-label*='More actions']",
        "button[aria-label*='more actions']",
        "button:has-text('More')",
    ]
    for selector in menu_selectors:
        btn = post.locator(selector).first
        if await btn.count() > 0:
            await btn.click()
            await human_pause(0.5)
            return True
    return False


async def click_delete_action(page) -> bool:
    action_selectors = [
        "div[role='menuitem']:has-text('Delete')",
        "div[role='menuitem']:has-text('Remove')",
        "button:has-text('Delete post')",
        "button:has-text('Delete')",
    ]
    for selector in action_selectors:
        action = page.locator(selector).first
        if await action.count() > 0:
            await action.click()
            await human_pause(0.4)
            return True
    return False


async def confirm_delete(page) -> bool:
    confirm_selectors = [
        "button:has-text('Delete')",
        "button:has-text('Confirm')",
        "button[aria-label*='Delete']",
    ]
    for selector in confirm_selectors:
        btn = page.locator(selector).first
        if await btn.count() > 0:
            await btn.click()
            await human_pause(0.8)
            return True
    return False


async def delete_posts(headed: bool, li_at_cookie: Optional[str], dry_run: bool, max_posts: int) -> int:
    deleted = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not headed)
        context = await browser.new_context(viewport={"width": 1440, "height": 1000})
        page = await context.new_page()

        await ensure_logged_in(page, li_at_cookie)

        # Feed cards container may vary. These selectors are intentionally broad.
        post_selector = "div.feed-shared-update-v2, li.profile-creator-shared-feed-update, div.occludable-update"

        while deleted < max_posts:
            await scroll_feed(page, times=1)
            posts = page.locator(post_selector)
            count = await posts.count()

            if count == 0:
                print("No posts found on page with current selectors.")
                break

            progress_this_pass = False

            for idx in range(count):
                if deleted >= max_posts:
                    break

                post = posts.nth(idx)

                try:
                    opened = await open_post_menu(post)
                    if not opened:
                        continue

                    if dry_run:
                        print(f"[dry-run] Would attempt delete for post index {idx}.")
                        await page.keyboard.press("Escape")
                        await human_pause(0.2)
                        deleted += 1
                        progress_this_pass = True
                        continue

                    clicked_delete = await click_delete_action(page)
                    if not clicked_delete:
                        await page.keyboard.press("Escape")
                        await human_pause(0.2)
                        continue

                    confirmed = await confirm_delete(page)
                    if confirmed:
                        deleted += 1
                        progress_this_pass = True
                        print(f"Deleted post #{deleted}")
                    else:
                        print("Delete option clicked but no confirmation button found.")

                except PlaywrightTimeoutError:
                    print("Timeout while processing a post; continuing.")
                    continue
                except Exception as exc:
                    print(f"Unexpected error on post index {idx}: {exc}")
                    continue

            if not progress_this_pass:
                print("No additional deletable posts found in this pass.")
                break

        await context.close()
        await browser.close()

    return deleted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delete LinkedIn posts from your own profile activity feed.")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode (recommended first run).")
    parser.add_argument("--dry-run", action="store_true", help="Do not delete; only simulate post processing.")
    parser.add_argument("--max-posts", type=int, default=20, help="Maximum posts to process (default: 20).")
    parser.add_argument(
        "--li-at",
        type=str,
        default=None,
        help="LinkedIn li_at session cookie value. If omitted, reads LI_AT env var.",
    )
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    li_at = args.li_at or os.getenv("LI_AT")

    if args.max_posts < 1:
        print("--max-posts must be >= 1")
        return 2

    try:
        deleted = await delete_posts(
            headed=args.headed,
            li_at_cookie=li_at,
            dry_run=args.dry_run,
            max_posts=args.max_posts,
        )
    except RuntimeError as err:
        print(f"Error: {err}")
        return 1

    if args.dry_run:
        print(f"Dry run completed. Processed up to {deleted} candidate posts.")
    else:
        print(f"Done. Deleted {deleted} posts.")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
