from typing import Dict, List, Any

from src.auditor.severity import HIGH, MEDIUM, LOW


def create_issue(
    issue: str,
    severity: str,
    field: str,
    recommendation: str
) -> Dict[str, str]:
    """
    Create a structured SEO issue.
    """

    return {
        "issue": issue,
        "severity": severity,
        "field": field,
        "recommendation": recommendation
    }


def safe_int(value: Any, default: int = 0) -> int:
    """
    Convert value to integer safely.
    """

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def audit_seo_data(seo_data: Dict) -> List[Dict[str, str]]:
    """
    Analyze extracted SEO data and return detected issues.
    """

    issues = []

    status_code = safe_int(seo_data.get("status_code"))

    title = seo_data.get("title")
    title_length = safe_int(seo_data.get("title_length"))

    meta_description = seo_data.get("meta_description")
    meta_description_length = safe_int(seo_data.get("meta_description_length"))

    h1_count = safe_int(seo_data.get("h1_count"))
    h2_count = safe_int(seo_data.get("h2_count"))

    canonical = seo_data.get("canonical")
    robots_meta = seo_data.get("robots_meta")

    word_count = safe_int(seo_data.get("word_count"))
    images_missing_alt = safe_int(seo_data.get("images_missing_alt"))

    # Status code rules
    if status_code and status_code != 200:
        issues.append(
            create_issue(
                issue="Non-200 Status Code",
                severity=HIGH,
                field="status_code",
                recommendation="Review this URL because it does not return a successful 200 status code."
            )
        )

    # Title rules
    if not title:
        issues.append(
            create_issue(
                issue="Missing Title",
                severity=HIGH,
                field="title",
                recommendation="Add a clear, unique, keyword-focused title tag for this page."
            )
        )
    else:
        if title_length < 30:
            issues.append(
                create_issue(
                    issue="Title Too Short",
                    severity=MEDIUM,
                    field="title",
                    recommendation="Make the title more descriptive and include the main page topic or keyword."
                )
            )

        if title_length > 60:
            issues.append(
                create_issue(
                    issue="Title Too Long",
                    severity=MEDIUM,
                    field="title",
                    recommendation="Shorten the title to make it clearer and more suitable for search results."
                )
            )

    # Meta description rules
    if not meta_description:
        issues.append(
            create_issue(
                issue="Missing Meta Description",
                severity=HIGH,
                field="meta_description",
                recommendation="Add a compelling meta description that summarizes the page and encourages clicks."
            )
        )
    else:
        if meta_description_length < 70:
            issues.append(
                create_issue(
                    issue="Meta Description Too Short",
                    severity=MEDIUM,
                    field="meta_description",
                    recommendation="Expand the meta description with a clearer benefit and page context."
                )
            )

        if meta_description_length > 160:
            issues.append(
                create_issue(
                    issue="Meta Description Too Long",
                    severity=MEDIUM,
                    field="meta_description",
                    recommendation="Shorten the meta description so it is more concise and search-result friendly."
                )
            )

    # H1 rules
    if h1_count == 0:
        issues.append(
            create_issue(
                issue="Missing H1",
                severity=HIGH,
                field="h1",
                recommendation="Add one clear H1 that describes the main topic of the page."
            )
        )

    if h1_count > 1:
        issues.append(
            create_issue(
                issue="Multiple H1 Tags",
                severity=MEDIUM,
                field="h1",
                recommendation="Use only one primary H1 and convert extra H1 tags to H2 or H3 if appropriate."
            )
        )

    # H2 rules
    if h2_count == 0:
        issues.append(
            create_issue(
                issue="No H2 Tags Found",
                severity=LOW,
                field="h2",
                recommendation="Add helpful H2 sections to improve page structure and readability."
            )
        )

    # Canonical rule
    if not canonical:
        issues.append(
            create_issue(
                issue="Missing Canonical",
                severity=MEDIUM,
                field="canonical",
                recommendation="Add a canonical tag to help search engines understand the preferred version of the page."
            )
        )

    # Robots meta rule
    if robots_meta and "noindex" in robots_meta.lower():
        issues.append(
            create_issue(
                issue="Page Marked as Noindex",
                severity=HIGH,
                field="robots_meta",
                recommendation="Review this page. If it should appear in search results, remove the noindex directive."
            )
        )

    # Content rule
    if word_count > 0 and word_count < 300:
        issues.append(
            create_issue(
                issue="Thin Content",
                severity=MEDIUM,
                field="word_count",
                recommendation="Improve the page content with more useful, relevant, and structured information."
            )
        )

    # Image alt rule
    if images_missing_alt > 0:
        issues.append(
            create_issue(
                issue="Images Missing Alt Text",
                severity=MEDIUM,
                field="images_missing_alt",
                recommendation="Add descriptive alt text to important images for accessibility and image SEO."
            )
        )

    return issues


def summarize_issues(issues: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Convert issue list into summary columns for the dashboard table.
    """

    high_count = 0
    medium_count = 0
    low_count = 0

    issue_names = []
    recommendations = []

    for issue in issues:
        severity = issue.get("severity")

        if severity == HIGH:
            high_count += 1
        elif severity == MEDIUM:
            medium_count += 1
        elif severity == LOW:
            low_count += 1

        issue_names.append(issue.get("issue", ""))
        recommendations.append(issue.get("recommendation", ""))

    return {
        "issues_count": len(issues),
        "high_issues": high_count,
        "medium_issues": medium_count,
        "low_issues": low_count,
        "issues": " | ".join(issue_names),
        "recommendations": " | ".join(recommendations)
    }