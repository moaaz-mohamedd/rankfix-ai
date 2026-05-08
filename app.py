import streamlit as st
import pandas as pd

from src.utils.validators import normalize_domain
from src.crawler.sitemap_parser import get_urls_from_sitemap
from src.crawler.page_fetcher import fetch_page
from src.extractor.seo_extractor import extract_seo_data


st.set_page_config(
    page_title="RankFix AI",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 RankFix AI - SEO Site Auditor")

st.write(
    "Enter a website domain and the tool will extract URLs from its sitemap, then analyze basic SEO tags."
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
                st.success(f"Found {len(urls)} URLs. Starting SEO extraction...")

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
                        results.append(seo_data)

                    else:
                        results.append({
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
                        })

                    progress_bar.progress((index + 1) / len(urls))

                df = pd.DataFrame(results)

                st.success("SEO extraction completed.")

                st.subheader("SEO Audit Results")
                st.dataframe(df, use_container_width=True)

        except ValueError as error:
            st.error(str(error))