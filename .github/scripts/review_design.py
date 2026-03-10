"""
Automated System Design Document Reviewer for GitHub PRs.

This script:
1. Reads design documents changed in the PR
2. Gets the PR diff for line mapping
3. Sends the document to Claude API for review
4. Posts review comments on specific PR lines
"""

import json
import os
import subprocess
import sys

import anthropic

# ── Config ──────────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
PR_NUMBER = os.environ["PR_NUMBER"]
REPO_FULL_NAME = os.environ["REPO_FULL_NAME"]
DESIGN_FILES = os.environ["DESIGN_FILES"]  # comma-separated
PR_HEAD_SHA = os.environ["PR_HEAD_SHA"]

MODEL = "claude-sonnet-4-5-20250514"

# ── Skill Files ─────────────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.join(SCRIPT_DIR, "..", "review-skill")

def load_skill_file(filename):
    """Load a skill file from .github/review-skill/."""
    path = os.path.join(SKILL_DIR, filename)
    with open(path) as f:
        return f.read()

def build_system_prompt():
    """Build the system prompt from the actual skill files."""
    review_skill = load_skill_file("review-system-design.md")
    writing_style = load_skill_file("writing-style-guide.md")

    return f"""You are a Senior Software Engineer and Technical Content Reviewer.

Below are your full review instructions and writing style guide. Follow them exactly.

--- REVIEW INSTRUCTIONS ---

{review_skill}

--- WRITING STYLE GUIDE ---

{writing_style}

--- OUTPUT FORMAT ---

You are reviewing a PR. You MUST output valid JSON only. No markdown, no explanation outside the JSON.

Output a JSON array of review comments. Each comment object has:
- "line": the line number in the file where the comment applies
- "body": the review comment text (short, conversational, following the PR Comment Style from the review instructions)
- "severity": "BLUNDER" or "ISSUE"

If you also want to leave a positive comment, use severity "PRAISE".

IMPORTANT: Only output BLUNDERS and ISSUES (and occasional PRAISE). Skip suggestions — those are not posted on PRs. This is specified in your review instructions.

Example output:
[
  {{"line": 45, "body": "Can we also mention the numbers here for availability? Something like 99.99% uptime.", "severity": "ISSUE"}},
  {{"line": 120, "body": "This API uses GET but it creates a resource. Should be POST.", "severity": "BLUNDER"}},
  {{"line": 200, "body": "Love this explanation of message queues. Very beginner-friendly!", "severity": "PRAISE"}}
]

If no issues found, output an empty array: []
"""

# ── Helpers ─────────────────────────────────────────────────────────────────────


def gh_api(method, endpoint, data=None):
    """Call GitHub API using gh CLI."""
    cmd = ["gh", "api", "-X", method, endpoint]
    if data:
        cmd.extend(["-f" if isinstance(v, str) else "-F" for k, v in data.items() for _ in [None]])
        # Build proper gh api flags
        cmd = ["gh", "api", "-X", method, endpoint]
        for k, v in data.items():
            if isinstance(v, (int, float)):
                cmd.extend(["-F", f"{k}={v}"])
            else:
                cmd.extend(["-f", f"{k}={v}"])

    result = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "GH_TOKEN": GITHUB_TOKEN})
    if result.returncode != 0:
        print(f"GitHub API error: {result.stderr}", file=sys.stderr)
        return None
    if result.stdout.strip():
        return json.loads(result.stdout)
    return None


def get_pr_diff(file_path):
    """Get the diff for a specific file in the PR."""
    result = subprocess.run(
        ["gh", "api", f"repos/{REPO_FULL_NAME}/pulls/{PR_NUMBER}",
         "-H", "Accept: application/vnd.github.v3.diff"],
        capture_output=True, text=True,
        env={**os.environ, "GH_TOKEN": GITHUB_TOKEN}
    )
    if result.returncode != 0:
        print(f"Failed to get PR diff: {result.stderr}", file=sys.stderr)
        return ""
    return result.stdout


def parse_diff_line_mapping(diff_text, target_file):
    """Parse the diff to find which lines in the new file are part of the diff.

    Returns a set of line numbers that are added/modified lines in the diff
    (these are the only lines we can comment on in a PR review).
    """
    lines_in_diff = set()
    in_target_file = False
    current_new_line = 0

    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            # Check if this diff section is for our target file
            in_target_file = target_file in line
            continue

        if not in_target_file:
            continue

        if line.startswith("@@"):
            # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
            try:
                parts = line.split("+")[1].split("@@")[0].strip()
                if "," in parts:
                    current_new_line = int(parts.split(",")[0])
                else:
                    current_new_line = int(parts)
            except (IndexError, ValueError):
                continue
            continue

        if line.startswith("-"):
            # Removed line — skip, doesn't exist in new file
            continue
        elif line.startswith("+"):
            # Added line — this is commentable
            lines_in_diff.add(current_new_line)
            current_new_line += 1
        else:
            # Context line
            current_new_line += 1

    return lines_in_diff


def find_nearest_diff_line(target_line, diff_lines):
    """Find the nearest line in the diff to the target line.

    We can only comment on lines that are part of the diff.
    """
    if not diff_lines:
        return None
    if target_line in diff_lines:
        return target_line
    # Find nearest line in the diff
    return min(diff_lines, key=lambda x: abs(x - target_line))


def read_file_content(file_path):
    """Read file content from the repo."""
    full_path = os.path.join(os.getcwd(), file_path)
    with open(full_path) as f:
        return f.read()


def review_document(file_path, file_content):
    """Send document to Claude API for review using the skill files."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Build system prompt from skill files
    system_prompt = build_system_prompt()

    # Add line numbers to content for reference
    numbered_content = ""
    for i, line in enumerate(file_content.split("\n"), 1):
        numbered_content += f"{i}: {line}\n"

    user_message = f"""Review this system design document. The file is: {file_path}

Here is the document with line numbers:

{numbered_content}

Output your review as a JSON array of comments. Each comment needs "line", "body", and "severity" fields.
Remember: keep comments short and conversational. Only BLUNDERS and ISSUES (and occasional PRAISE). No suggestions."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    # Extract JSON from response
    response_text = response.content[0].text.strip()

    # Handle case where response is wrapped in markdown code block
    if response_text.startswith("```"):
        # Remove ```json and ``` markers
        lines = response_text.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        response_text = "\n".join(lines)

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        print(f"Failed to parse Claude response as JSON: {response_text[:500]}", file=sys.stderr)
        return []


def post_review_comments(comments, file_path, diff_lines):
    """Post review comments on the PR using the GitHub pull request review API."""
    if not comments:
        print("No comments to post.")
        return

    # Build review comments array for the GitHub review API
    review_comments = []

    for comment in comments:
        line = comment.get("line")
        body = comment.get("body", "")
        severity = comment.get("severity", "ISSUE")

        if not line or not body:
            continue

        # Find nearest line in the diff we can comment on
        actual_line = find_nearest_diff_line(line, diff_lines)
        if actual_line is None:
            print(f"  Skipping comment (no diff lines available): {body[:60]}...")
            continue

        # Add severity prefix
        if severity == "BLUNDER":
            prefixed_body = f"**BLUNDER**: {body}"
        elif severity == "PRAISE":
            prefixed_body = body
        else:
            prefixed_body = body

        review_comments.append({
            "path": file_path,
            "line": actual_line,
            "body": prefixed_body,
        })

    if not review_comments:
        print("No comments could be mapped to diff lines.")
        return

    # Count severities for the review summary
    blunder_count = sum(1 for c in comments if c.get("severity") == "BLUNDER")
    issue_count = sum(1 for c in comments if c.get("severity") == "ISSUE")
    praise_count = sum(1 for c in comments if c.get("severity") == "PRAISE")

    # Determine review event type
    if blunder_count > 0:
        event = "REQUEST_CHANGES"
        summary = f"Found **{blunder_count} blunder(s)** and **{issue_count} issue(s)**. Please address the blunders before merging."
    elif issue_count > 0:
        event = "COMMENT"
        summary = f"Found **{issue_count} issue(s)** to address. No critical blunders."
    else:
        event = "COMMENT"
        summary = "Looks good overall!"

    if praise_count > 0:
        summary += f" ({praise_count} thing(s) done really well!)"

    summary += "\n\n*— Automated review by SweetCodey Design Reviewer*"

    # Post the review using gh CLI
    review_payload = {
        "commit_id": PR_HEAD_SHA,
        "body": summary,
        "event": event,
        "comments": review_comments,
    }

    payload_json = json.dumps(review_payload)

    result = subprocess.run(
        ["gh", "api", "-X", "POST",
         f"repos/{REPO_FULL_NAME}/pulls/{PR_NUMBER}/reviews",
         "--input", "-"],
        input=payload_json,
        capture_output=True, text=True,
        env={**os.environ, "GH_TOKEN": GITHUB_TOKEN}
    )

    if result.returncode != 0:
        print(f"Failed to post review: {result.stderr}", file=sys.stderr)
        # Fallback: post individual comments
        print("Falling back to individual comments...")
        for rc in review_comments:
            gh_api("POST", f"repos/{REPO_FULL_NAME}/pulls/{PR_NUMBER}/comments", {
                "body": rc["body"],
                "commit_id": PR_HEAD_SHA,
                "path": rc["path"],
                "line": rc["line"],
            })
    else:
        print(f"Review posted successfully with {len(review_comments)} comments.")


# ── Deduplication ───────────────────────────────────────────────────────────────


def dismiss_previous_bot_reviews():
    """Dismiss previous reviews posted by this bot to avoid duplicate comments.

    Fetches all reviews on the PR, finds ones posted by github-actions[bot]
    with our signature, and dismisses them.
    """
    result = subprocess.run(
        ["gh", "api", f"repos/{REPO_FULL_NAME}/pulls/{PR_NUMBER}/reviews",
         "--paginate"],
        capture_output=True, text=True,
        env={**os.environ, "GH_TOKEN": GITHUB_TOKEN}
    )
    if result.returncode != 0:
        print(f"Could not fetch existing reviews: {result.stderr}", file=sys.stderr)
        return

    try:
        reviews = json.loads(result.stdout)
    except json.JSONDecodeError:
        return

    for review in reviews:
        user = review.get("user", {}).get("login", "")
        body = review.get("body", "")
        review_id = review.get("id")
        state = review.get("state", "")

        # Match our bot's reviews by the signature in the summary
        if "SweetCodey Design Reviewer" in body and review_id:
            if state in ("CHANGES_REQUESTED", "COMMENTED"):
                # Dismiss the review
                dismiss_result = subprocess.run(
                    ["gh", "api", "-X", "PUT",
                     f"repos/{REPO_FULL_NAME}/pulls/{PR_NUMBER}/reviews/{review_id}/dismissals",
                     "-f", "message=Superseded by new review on latest commit."],
                    capture_output=True, text=True,
                    env={**os.environ, "GH_TOKEN": GITHUB_TOKEN}
                )
                if dismiss_result.returncode == 0:
                    print(f"  Dismissed previous review {review_id}")
                else:
                    print(f"  Could not dismiss review {review_id}: {dismiss_result.stderr}",
                          file=sys.stderr)


# ── Main ────────────────────────────────────────────────────────────────────────


def main():
    design_files = [f.strip() for f in DESIGN_FILES.split(",") if f.strip()]
    print(f"Design files to review: {design_files}")

    # Dismiss previous bot reviews to avoid duplicate comments
    print("Checking for previous bot reviews to dismiss...")
    dismiss_previous_bot_reviews()

    # Get full PR diff once
    diff_text = get_pr_diff("")

    for file_path in design_files:
        print(f"\n{'='*60}")
        print(f"Reviewing: {file_path}")
        print(f"{'='*60}")

        # Read file content
        try:
            content = read_file_content(file_path)
        except FileNotFoundError:
            print(f"  File not found: {file_path}. Skipping.")
            continue

        # Parse diff to know which lines we can comment on
        diff_lines = parse_diff_line_mapping(diff_text, file_path)
        print(f"  Lines in diff: {len(diff_lines)}")

        if not diff_lines:
            print("  No diff lines found for this file. Skipping.")
            continue

        # Review the document
        print("  Sending to Claude for review...")
        comments = review_document(file_path, content)
        print(f"  Got {len(comments)} comments from review.")

        for c in comments:
            severity = c.get("severity", "?")
            line = c.get("line", "?")
            body = c.get("body", "")[:80]
            print(f"    [{severity}] L{line}: {body}...")

        # Post comments on the PR
        print("  Posting comments to PR...")
        post_review_comments(comments, file_path, diff_lines)

    print("\nDone!")


if __name__ == "__main__":
    main()
