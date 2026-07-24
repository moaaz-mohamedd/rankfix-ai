from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from samples.sample_pages import SAMPLE_PAGES
from src.extractor.seo_extractor import extract_seo_data
from src.auditor.rules_engine import audit_seo_data, summarize_issues


results = []

for page in SAMPLE_PAGES:
    seo_data = extract_seo_data(
        url=page["url"],
        html=page["html"]
    )

    seo_data["status_code"] = 200
    seo_data["error"] = None

    issues = audit_seo_data(seo_data)
    issue_summary = summarize_issues(issues)

    seo_data.update(issue_summary)

    results.append(seo_data)


df = pd.DataFrame(results)

display_columns = [
    "url",
    "title",
    "title_length",
    "meta_description",
    "meta_description_length",
    "h1",
    "h1_count",
    "h2_count",
    "canonical",
    "robots_meta",
    "word_count",
    "total_images",
    "images_missing_alt",
    "issues_count",
    "high_issues",
    "medium_issues",
    "low_issues",
    "issues",
    "recommendations"
]

print("\nSEO Audit Sample Results")
print("=" * 80)

for _, row in df.iterrows():
    print(f"\nURL: {row['url']}")
    print(f"Title: {row['title']}")
    print(f"Title Length: {row['title_length']}")
    print(f"Meta Length: {row['meta_description_length']}")
    print(f"H1 Count: {row['h1_count']}")
    print(f"Word Count: {row['word_count']}")
    print(f"Images Missing Alt: {row['images_missing_alt']}")
    print(f"Issues Count: {row['issues_count']}")
    print(f"High: {row['high_issues']} | Medium: {row['medium_issues']} | Low: {row['low_issues']}")
    print("Issues:")

    issues = str(row["issues"]).split(" | ")

    for issue in issues:
        print(f"  - {issue}")

    print("-" * 80)