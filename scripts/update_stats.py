"""
update_stats.py  (fixed)
------------------------
Fetches live stats from TryHackMe, HackTheBox, CyberDefenders (scrape),
and GitHub, then rewrites the stats sections in README.md.

Each platform section in README.md is wrapped in HTML comment markers:
  <!-- PLATFORM_START --> ... <!-- PLATFORM_END -->
This script replaces everything between those markers on every run.
"""

import os
import re
import sys
import json
import requests
from datetime import datetime, timezone

# ── Config from environment variables (set as GitHub Secrets) ──────────────
THM_USERNAME = os.environ.get("THM_USERNAME", "")
HTB_USERNAME = os.environ.get("HTB_USERNAME", "")
HTB_USER_ID  = os.environ.get("HTB_USER_ID", "")
CD_USERNAME  = os.environ.get("CD_USERNAME", "")
GH_USERNAME  = os.environ.get("GH_USERNAME", "")
GH_TOKEN     = os.environ.get("GH_TOKEN", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "application/json, text/html,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

# ── Helpers ────────────────────────────────────────────────────────────────

def replace_section(content: str, marker: str, new_block: str) -> str:
    pattern = rf"(<!-- {marker}_START -->).*?(<!-- {marker}_END -->)"
    replacement = rf"\1\n{new_block}\n\2"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)


def safe_get(url: str, headers: dict = None, timeout: int = 12):
    try:
        h = {**HEADERS, **(headers or {})}
        r = requests.get(url, timeout=timeout, headers=h)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  WARNING: Request failed [{url}]: {e}")
        return None


def safe_get_text(url: str, headers: dict = None, timeout: int = 12):
    try:
        h = {**HEADERS, **(headers or {})}
        r = requests.get(url, timeout=timeout, headers=h)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"  WARNING: Request failed [{url}]: {e}")
        return None

# ── TryHackMe ─────────────────────────────────────────────────────────────

def fetch_tryhackme() -> str:
    print("Fetching TryHackMe stats...")
    if not THM_USERNAME:
        return "_TryHackMe username not set._"

    rank   = "N/A"
    points = "N/A"
    rooms  = "N/A"
    streak = "N/A"

    thm_headers = {
        "Referer": "https://tryhackme.com/",
        "Origin":  "https://tryhackme.com",
    }

    # Endpoint 1: rank
    data = safe_get(f"https://tryhackme.com/api/user/rank/{THM_USERNAME}", headers=thm_headers)
    if data:
        rank = str(data.get("userRank", "N/A"))

    # Endpoint 2: full profile
    profile = safe_get(f"https://tryhackme.com/api/user/{THM_USERNAME}", headers=thm_headers)
    if profile:
        p = profile.get("userProfile", profile)
        points = str(p.get("points",         p.get("totalPoints",    "N/A")))
        rooms  = str(p.get("completedRooms", p.get("roomsCompleted", "N/A")))
        streak = str(p.get("streak",         p.get("currentStreak",  "N/A")))

    # Fallback: scrape __NEXT_DATA__ from profile page
    if all(v == "N/A" for v in [points, rooms, streak]):
        print("  Falling back to THM profile page scrape...")
        html = safe_get_text(f"https://tryhackme.com/p/{THM_USERNAME}", headers=thm_headers)
        if html:
            match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
            if match:
                try:
                    nd    = json.loads(match.group(1))
                    props = nd.get("props", {}).get("pageProps", {})
                    user  = props.get("user", props.get("userProfile", {}))
                    rank   = str(user.get("userRank",       user.get("rank",          rank)))
                    points = str(user.get("points",         user.get("score",         points)))
                    rooms  = str(user.get("completedRooms", user.get("rooms",         rooms)))
                    streak = str(user.get("streak",         user.get("currentStreak", streak)))
                except Exception as e:
                    print(f"  THM JSON parse failed: {e}")

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
    print("Fetching HackTheBox stats...")
    if not HTB_USER_ID:
        return "_HackTheBox user ID not set._"

    rank      = "N/A"
    points    = "N/A"
    user_owns = "N/A"
    root_owns = "N/A"
    challenges= "N/A"
    respect   = "N/A"

    htb_headers = {
        "Referer": "https://www.hackthebox.com/",
        "Accept":  "application/json, text/plain, */*",
    }

    data = safe_get(f"https://www.hackthebox.com/api/v4/profile/{HTB_USER_ID}", headers=htb_headers)

    if data and "profile" in data:
        p         = data["profile"]
        rank      = str(p.get("ranking",        "N/A"))
        points    = str(p.get("points",         "N/A"))
        user_owns = str(p.get("user_owns",      "N/A"))
        root_owns = str(p.get("system_owns",    "N/A"))
        challenges= str(p.get("challenge_owns", "N/A"))
        respect   = str(p.get("respects",       "N/A"))

    # Fallback: try the overview endpoint
    if all(v == "N/A" for v in [rank, points, user_owns]):
        print("  Falling back to HTB overview endpoint...")
        data2 = safe_get(f"https://www.hackthebox.com/api/v4/profile/overview/{HTB_USER_ID}", headers=htb_headers)
        if data2:
            p         = data2.get("profile", data2)
            rank      = str(p.get("ranking",        rank))
            points    = str(p.get("points",         points))
            user_owns = str(p.get("user_owns",      user_owns))
            root_owns = str(p.get("system_owns",    root_owns))
            challenges= str(p.get("challenge_owns", challenges))
            respect   = str(p.get("respects",       respect))

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
    print("Fetching CyberDefenders stats (scrape)...")
    if not CD_USERNAME:
        return "_CyberDefenders username not set._"

    rank   = "N/A"
    score  = "N/A"
    solved = "N/A"

    cd_headers = {
        "Referer": "https://cyberdefenders.org/",
        "Accept":  "text/html,application/xhtml+xml,*/*",
    }

    html = safe_get_text(f"https://cyberdefenders.org/p/{CD_USERNAME}", headers=cd_headers)

    if html:
        # Try __NEXT_DATA__ JSON first
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if match:
            try:
                nd    = json.loads(match.group(1))
                props = nd.get("props", {}).get("pageProps", {})
                user  = props.get("profile", props.get("user", props))
                rank   = str(user.get("rank",   user.get("ranking",    rank)))
                score  = str(user.get("score",  user.get("points",     score)))
                solved = str(user.get("solved", user.get("challenges", solved)))
            except Exception as e:
                print(f"  CD JSON parse failed: {e}")

        # Regex fallback
        if rank == "N/A":
            m = re.search(r'"rank"\s*:\s*"?([^",}]+)"?', html)
            if m: rank = m.group(1).strip()
        if score == "N/A":
            m = re.search(r'"score"\s*:\s*(\d+)', html)
            if m: score = m.group(1).strip()

    lines = [
        "### 🔵 CyberDefenders\n",
        f"[![CyberDefenders](https://img.shields.io/badge/CyberDefenders-Profile-1A6FB5?style=flat-square&logo=shield&logoColor=white)](https://cyberdefenders.org/p/{CD_USERNAME})\n",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| 🏆 Rank | {rank} |",
        f"| ⭐ Score | {score} |",
        f"| 🧩 Challenges Solved | {solved} |",
        "",
        "> ℹ️ CyberDefenders has no public API — stats scraped from your public profile page.",
    ]
    return "\n".join(lines)

# ── GitHub ────────────────────────────────────────────────────────────────

def fetch_github() -> str:
    print("Fetching GitHub stats...")
    if not GH_USERNAME:
        return "_GitHub username not set._"

    gh_headers = {**HEADERS, "Accept": "application/vnd.github+json"}
    if GH_TOKEN:
        gh_headers["Authorization"] = f"Bearer {GH_TOKEN}"

    user  = safe_get(f"https://api.github.com/users/{GH_USERNAME}", headers=gh_headers)
    repos = safe_get(
        f"https://api.github.com/users/{GH_USERNAME}/repos?per_page=100&type=owner",
        headers=gh_headers
    )

    followers   = "N/A"
    following   = "N/A"
    pub_repos   = "N/A"
    total_stars = 0

    if user:
        followers = str(user.get("followers",    "N/A"))
        following = str(user.get("following",    "N/A"))
        pub_repos = str(user.get("public_repos", "N/A"))

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
        print(f"ERROR: {readme_path} not found. Run from repo root.")
        sys.exit(1)

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    content = replace_section(content, "THM",        fetch_tryhackme())
    content = replace_section(content, "HTB",        fetch_hackthebox())
    content = replace_section(content, "CD",         fetch_cyberdefenders())
    content = replace_section(content, "GITHUB",     fetch_github())
    content = replace_section(content, "UPDATED_AT", f"_Last updated: **{now}** by GitHub Actions_")

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"README.md updated at {now}")

if __name__ == "__main__":
    main()
