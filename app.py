import streamlit as st
import pandas as pd

from src.utils.validators import normalize_domain
from src.crawler.sitemap_parser import get_urls_from_sitemap


st.set_page_config(
    page_title="RankFix AI",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 RankFix AI - SEO Site Auditor")

st.write(
    "Enter a website domain and the tool will extract URLs from its sitemap."
)

domain_input = st.text_input(
    "Website Domain",
    placeholder="example.com"
)

max_urls = st.slider(
    "Maximum URLs to extract",
    min_value=10,
    max_value=100,
    value=50,
    step=10
)

if st.button("Start Sitemap Crawl"):
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
                st.success(f"Found {len(urls)} URLs.")

                df = pd.DataFrame({
                    "URL": urls
                })

                st.dataframe(df, use_container_width=True)

        except ValueError as error:
            st.error(str(error))