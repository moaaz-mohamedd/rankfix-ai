SAMPLE_PAGES = [
    {
        "url": "https://example.com/good-seo-page",
        "html": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SEO Services for Small Businesses in Egypt</title>
            <meta name="description" content="Discover professional SEO services that help small businesses improve Google visibility, attract qualified traffic, and grow online.">
            <link rel="canonical" href="https://example.com/good-seo-page">
        </head>
        <body>
            <h1>SEO Services for Small Businesses</h1>
            <h2>Why SEO Matters</h2>
            <p>SEO helps businesses improve visibility, attract organic traffic, and increase qualified leads from search engines.</p>
            <h2>Our SEO Process</h2>
            <p>We analyze your website, optimize technical SEO, improve content quality, and build a strong keyword strategy.</p>
            <img src="seo-image.jpg" alt="SEO strategy dashboard">
        </body>
        </html>
        """
    },
    {
        "url": "https://example.com/missing-meta-h1",
        "html": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Home</title>
        </head>
        <body>
            <p>We provide marketing services for companies.</p>
            <p>Contact us today.</p>
            <img src="banner.jpg">
        </body>
        </html>
        """
    },
    {
        "url": "https://example.com/very-long-title",
        "html": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>This Is a Very Long SEO Title That Exceeds the Recommended Length and May Be Truncated in Search Results</title>
            <meta name="description" content="Short meta.">
        </head>
        <body>
            <h1>Digital Marketing Services</h1>
            <h2>About Our Services</h2>
            <p>We help brands improve digital performance through SEO, content, and paid media strategies.</p>
            <img src="marketing.jpg" alt="">
        </body>
        </html>
        """
    },
    {
        "url": "https://example.com/noindex-thin-content",
        "html": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SEO Audit</title>
            <meta name="description" content="SEO audit services for websites with technical and content analysis.">
            <meta name="robots" content="noindex, nofollow">
        </head>
        <body>
            <h1>SEO Audit</h1>
            <p>SEO audit.</p>
            <img src="audit1.jpg">
            <img src="audit2.jpg">
        </body>
        </html>
        """
    }
]