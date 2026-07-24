from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from samples.sample_pages import SAMPLE_PAGES
from src.extractor.seo_extractor import extract_seo_data
from src.auditor.rules_engine import audit_seo_data, summarize_issues
from src.ai.seo_recommender import generate_seo_recommendations


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

    ai_result = generate_seo_recommendations(
        seo_data=seo_data,
        issues_text=seo_data.get("issues", "")
    )

    seo_data.update({
        "ai_title_score": ai_result.get("title_score"),
        "ai_meta_score": ai_result.get("meta_score"),
        "ai_suggested_title": ai_result.get("suggested_title"),
        "ai_suggested_meta_description": ai_result.get("suggested_meta_description"),
        "ai_suggested_h1": ai_result.get("suggested_h1"),
        "ai_reason": ai_result.get("reason"),
        "ai_error": ai_result.get("ai_error"),
    })

    results.append(seo_data)


df = pd.DataFrame(results)

print("\nAI SEO Recommendation Results")
print("=" * 80)

for _, row in df.iterrows():
    print(f"\nURL: {row['url']}")
    print(f"Current Title: {row['title']}")
    print(f"Current Meta: {row['meta_description']}")
    print(f"Issues: {row['issues']}")

    print("\nAI Recommendations:")
    print(f"Title Score: {row['ai_title_score']}")
    print(f"Meta Score: {row['ai_meta_score']}")
    print(f"Suggested Title: {row['ai_suggested_title']}")
    print(f"Suggested Meta: {row['ai_suggested_meta_description']}")
    print(f"Suggested H1: {row['ai_suggested_h1']}")
    print(f"Reason: {row['ai_reason']}")

    if row["ai_error"]:
        print(f"AI Error: {row['ai_error']}")

    print("-" * 80)