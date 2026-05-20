import streamlit as st
import pandas as pd

from src.utils.validators import normalize_domain
from src.crawler.sitemap_parser import get_urls_from_sitemap
from src.crawler.page_fetcher import fetch_page
from src.extractor.seo_extractor import extract_seo_data
from src.auditor.rules_engine import audit_seo_data, summarize_issues
from src.reports.excel_exporter import create_excel_report


st.set_page_config(
    page_title="RankFix AI",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 RankFix AI - SEO Site Auditor")

st.write(
    "Enter a website domain and the tool will extract URLs from its sitemap, analyze SEO tags, detect on-page SEO issues, and export an Excel report."
)

domain_input = st.text_input(
    "Website Domain",
    placeholder="example.com"
)

max_urls = st.slider(
    "Maximum URLs to analyze",
    min_value=5,
    max_value=100,
    value=10,
    step=5
)

if st.button("Start SEO Audit"):
    if not domain_input:
        st.warning("Please enter a domain first.")
    else:
        try:
            domain = normalize_domain(domain_input)

            st.info(f"Scanning sitemap for: {domain}")

            urls = get_urls_from_sitemap(domain, max_urls=max_urls)

            if not urls:
                st.error("No URLs found. The website may not have a public sitemap.")
            else:
                st.success(f"Found {len(urls)} URLs. Starting SEO audit...")

                results = []

                progress_bar = st.progress(0)

                for index, url in enumerate(urls):
                    page_response = fetch_page(url)

                    if page_response["html"]:
                        seo_data = extract_seo_data(
                            url=page_response["final_url"] or url,
                            html=page_response["html"]
                        )

                        seo_data["status_code"] = page_response["status_code"]
                        seo_data["error"] = None

                    else:
                        seo_data = {
                            "url": url,
                            "status_code": page_response["status_code"],
                            "title": None,
                            "title_length": 0,
                            "meta_description": None,
                            "meta_description_length": 0,
                            "h1_count": 0,
                            "h1": None,
                            "h2_count": 0,
                            "canonical": None,
                            "robots_meta": None,
                            "word_count": 0,
                            "total_images": 0,
                            "images_missing_alt": 0,
                            "error": page_response["error"]
                        }

                    issues = audit_seo_data(seo_data)
                    issue_summary = summarize_issues(issues)

                    seo_data.update(issue_summary)

                    results.append(seo_data)

                    progress_bar.progress((index + 1) / len(urls))

                df = pd.DataFrame(results)

                st.success("SEO audit completed.")

                st.subheader("Audit Summary")

                total_pages = len(df)
                total_issues = int(df["issues_count"].sum())
                total_high = int(df["high_issues"].sum())
                total_medium = int(df["medium_issues"].sum())
                total_low = int(df["low_issues"].sum())

                col1, col2, col3, col4, col5 = st.columns(5)

                col1.metric("Pages", total_pages)
                col2.metric("Total Issues", total_issues)
                col3.metric("High", total_high)
                col4.metric("Medium", total_medium)
                col5.metric("Low", total_low)

                st.subheader("SEO Audit Results")

                display_columns = [
                    "url",
                    "status_code",
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
                    "recommendations",
                    "error"
                ]

                report_df = df[display_columns]

                st.dataframe(
                    report_df,
                    use_container_width=True
                )

                excel_file = create_excel_report(report_df)

                st.download_button(
                    label="Download Excel Report",
                    data=excel_file,
                    file_name="rankfix_ai_seo_audit.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except ValueError as error:
            st.error(str(error))