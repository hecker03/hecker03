"""
update_stats.py
---------------
Fetches live stats from TryHackMe, HackTheBox, CyberDefenders (scrape),
and GitHub, then rewrites the stats sections in README.md.

Each platform section in README.md is wrapped in HTML comment markers:
  <!-- PLATFORM_START --> ... <!-- PLATFORM_END -->
This script replaces everything between those markers on every run.
"""

import os
import re
import sys
import requests
from datetime import datetime, timezone

# ── Config from environment variables (set as GitHub Secrets) ──────────────
THM_USERNAME = os.environ.get("THM_USERNAME", "")
HTB_USERNAME = os.environ.get("HTB_USERNAME", "")
HTB_USER_ID  = os.environ.get("HTB_USER_ID", "")
CD_USERNAME  = os.environ.get("CD_USERNAME", "")
GH_USERNAME  = os.environ.get("GH_USERNAME", "")
GH_TOKEN     = os.environ.get("GH_TOKEN", "")

HEADERS = {"User-Agent": "Mozilla/5.0 (GitHub Profile Bot)"}

# ── Helpers ────────────────────────────────────────────────────────────────

def replace_section(content: str, marker: str, new_block: str) -> str:
    """Replace content between <!-- MARKER_START --> and <!-- MARKER_END -->."""
    pattern = rf"(<!-- {marker}_START -->).*?(<!-- {marker}_END -->)"
    replacement = rf"\1\n{new_block}\n\2"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)


def badge(label: str, message: str, color: str, logo: str = "", style: str = "flat-square") -> str:
    """Generate a shields.io badge URL as markdown."""
    msg   = requests.utils.quote(message, safe="")
    lbl   = requests.utils.quote(label,   safe="")
    logo_part = f"&logo={logo}" if logo else ""
    return f"![{label}](https://img.shields.io/badge/{lbl}-{msg}-{color}?style={style}{logo_part}&logoColor=white)"


def safe_get(url: str, **kwargs) -> dict | None:
    """GET request with timeout; returns JSON dict or None on failure."""
    try:
        r = requests.get(url, timeout=10, headers=HEADERS, **kwargs)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  ⚠️  Request failed for {url}: {e}")
        return None

# ── TryHackMe ─────────────────────────────────────────────────────────────

def fetch_tryhackme() -> str:
    print("📡 Fetching TryHackMe stats...")
    if not THM_USERNAME:
        return "_TryHackMe username not set._"

    data = safe_get(f"https://tryhackme.com/api/user/rank/{THM_USERNAME}")
    profile = safe_get(f"https://tryhackme.com/api/user/{THM_USERNAME}")

    rank   = "N/A"
    points = "N/A"
    rooms  = "N/A"
    streak = "N/A"

    if data:
        rank = str(data.get("userRank", "N/A"))

    if profile:
        p = profile.get("userProfile", profile)  # API shape varies
        points = str(p.get("points", p.get("totalPoints", "N/A")))
        rooms  = str(p.get("completedRooms", "N/A"))
        streak = str(p.get("streak",          "N/A"))

    lines = [
        "### 🔴 TryHackMe\n",
        f"[![TryHackMe Badge](https://tryhackme-badge.fly.dev/?username={THM_USERNAME})](https://tryhackme.com/p/{THM_USERNAME})\n",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| 🏆 Global Rank | #{rank} |",
        f"| ⭐ Points | {points} |",
        f"| 🚪 Rooms Completed | {rooms} |",
        f"| 🔥 Streak | {streak} days |",
    ]
    return "\n".join(lines)

# ── HackTheBox ────────────────────────────────────────────────────────────

def fetch_hackthebox() -> str:
    print("📡 Fetching HackTheBox stats...")
    if not HTB_USER_ID:
        return "_HackTheBox user ID not set._"

    data = safe_get(f"https://www.hackthebox.com/api/v4/profile/{HTB_USER_ID}")

    rank      = "N/A"
    points    = "N/A"
    user_owns = "N/A"
    root_owns = "N/A"
    challenges= "N/A"
    respect   = "N/A"

    if data and "profile" in data:
        p          = data["profile"]
        rank       = p.get("ranking",         "N/A")
        points     = p.get("points",          "N/A")
        user_owns  = p.get("user_owns",       "N/A")
        root_owns  = p.get("system_owns",     "N/A")
        challenges = p.get("challenge_owns",  "N/A")
        respect    = p.get("respects",        "N/A")

    lines = [
        "### 🟢 HackTheBox\n",
        f"<img src=\"https://www.hackthebox.eu/badge/image/{HTB_USER_ID}\" alt=\"HackTheBox Badge\" />\n",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| 🏆 Global Rank | #{rank} |",
        f"| ⭐ Points | {points} |",
        f"| 💻 User Owns | {user_owns} |",
        f"| 👑 Root / System Owns | {root_owns} |",
        f"| 🧩 Challenges Solved | {challenges} |",
        f"| 👏 Respects | {respect} |",
    ]
    return "\n".join(lines)

# ── CyberDefenders ────────────────────────────────────────────────────────

def fetch_cyberdefenders() -> str:
    """
    CyberDefenders has no public API.
    We attempt a lightweight scrape of the public profile page.
    Falls back gracefully to a static badge if scraping fails.
    """
    print("📡 Fetching CyberDefenders stats (scrape)...")
    if not CD_USERNAME:
        return "_CyberDefenders username not set._"

    rank  = "N/A"
    score = "N/A"
    badge_label = "CyberDefenders"

    try:
        from html.parser import HTMLParser

        class CDParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.in_rank  = False
                self.in_score = False
                self.rank     = "N/A"
                self.score    = "N/A"

            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs)
                cls = attrs_dict.get("class", "")
                # Adjust selectors if CyberDefenders changes their markup
                if "rank" in cls.lower():
                    self.in_rank = True
                if "score" in cls.lower() or "point" in cls.lower():
                    self.in_score = True

            def handle_data(self, data):
                data = data.strip()
                if self.in_rank and data:
                    self.rank = data
                    self.in_rank = False
                if self.in_score and data:
                    self.score = data
                    self.in_score = False

        url = f"https://cyberdefenders.org/p/{CD_USERNAME}"
        r   = requests.get(url, timeout=12, headers=HEADERS)
        r.raise_for_status()
        parser = CDParser()
        parser.feed(r.text)
        rank  = parser.rank
        score = parser.score

    except Exception as e:
        print(f"  ⚠️  CyberDefenders scrape failed: {e}")

    lines = [
        "### 🔵 CyberDefenders\n",
        f"[![CyberDefenders](https://img.shields.io/badge/CyberDefenders-Profile-1A6FB5?style=flat-square&logo=shield&logoColor=white)](https://cyberdefenders.org/p/{CD_USERNAME})\n",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| 🏆 Rank | {rank} |",
        f"| ⭐ Score | {score} |",
        "",
        "> ℹ️ CyberDefenders has no public API — stats are scraped from your public profile page.",
    ]
    return "\n".join(lines)

# ── GitHub ────────────────────────────────────────────────────────────────

def fetch_github() -> str:
    print("📡 Fetching GitHub stats...")
    if not GH_USERNAME:
        return "_GitHub username not set._"

    auth_headers = {**HEADERS}
    if GH_TOKEN:
        auth_headers["Authorization"] = f"Bearer {GH_TOKEN}"

    user  = safe_get(f"https://api.github.com/users/{GH_USERNAME}", headers=auth_headers)
    repos = safe_get(f"https://api.github.com/users/{GH_USERNAME}/repos?per_page=100&type=owner", headers=auth_headers)

    followers  = "N/A"
    following  = "N/A"
    pub_repos  = "N/A"
    total_stars = 0

    if user:
        followers = user.get("followers",         "N/A")
        following = user.get("following",         "N/A")
        pub_repos = user.get("public_repos",      "N/A")

    if repos and isinstance(repos, list):
        total_stars = sum(r.get("stargazers_count", 0) for r in repos)

    lines = [
        "### 🐙 GitHub\n",
        f"![GitHub Stats](https://github-readme-stats.vercel.app/api?username={GH_USERNAME}&show_icons=true&theme=dark&hide_border=true&count_private=true)\n",
        f"[![GitHub Streak](https://streak-stats.demolab.com?user={GH_USERNAME}&theme=dark&hide_border=true)](https://git.io/streak-stats)\n",
        f"![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username={GH_USERNAME}&layout=compact&theme=dark&hide_border=true)\n",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| 👥 Followers | {followers} |",
        f"| 👤 Following | {following} |",
        f"| 📦 Public Repos | {pub_repos} |",
        f"| ⭐ Total Stars | {total_stars} |",
    ]
    return "\n".join(lines)

# ── Main ──────────────────────────────────────────────────────────────────

def main():
    readme_path = "README.md"

    if not os.path.exists(readme_path):
        print(f"❌ {readme_path} not found. Run this script from the repo root.")
        sys.exit(1)

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    content = replace_section(content, "THM",       fetch_tryhackme())
    content = replace_section(content, "HTB",       fetch_hackthebox())
    content = replace_section(content, "CD",        fetch_cyberdefenders())
    content = replace_section(content, "GITHUB",    fetch_github())
    content = replace_section(content, "UPDATED_AT", f"_⏱ Last updated: **{now}** by GitHub Actions_")

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ README.md updated at {now}")

if __name__ == "__main__":
    main()
