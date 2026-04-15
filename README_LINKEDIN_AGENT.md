# LinkedIn Delete-Posts Agent

This repository now includes `linkedin_delete_posts_agent.py`, a Playwright-based automation script that can delete posts from **your own** LinkedIn activity feed.

## 1) Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-linkedin-agent.txt
python -m playwright install chromium
```

## 2) Get your `li_at` session cookie

1. Log into LinkedIn in your browser.
2. Open DevTools → Application/Storage → Cookies → `https://www.linkedin.com`.
3. Copy the value of the `li_at` cookie.

> Keep this cookie secret; it authenticates your account.

## 3) Run in safe mode first

```bash
export LI_AT='paste_cookie_here'
python linkedin_delete_posts_agent.py --headed --dry-run --max-posts 10
```

## 4) Perform deletion

```bash
python linkedin_delete_posts_agent.py --headed --max-posts 100
```

## Notes

- The script uses UI selectors that LinkedIn may change at any time.
- Start with a small `--max-posts` to verify behavior.
- If selectors stop working, update the selector list in:
  - `open_post_menu`
  - `click_delete_action`
  - `confirm_delete`
