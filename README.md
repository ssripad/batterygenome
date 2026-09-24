# Battery Industry Genome™

Live at **[batterygenome.net](https://batterygenome.net)**.

16 domains · 170 application segments · ~$365B of 2025 battery demand, mapped by
application, market size (audited, with ranges), an 8-axis requirement fingerprint,
price band, ranked top-5 suppliers, and a reference cell design per segment.
One self-contained HTML file - no build, no dependencies.

## Structure
- `index.html` - the entire genome (app + embedded data)
- `og-image.png`, `apple-touch-icon.png`, `favicon.ico` - icons and the home link preview
- `s/<id>/` - share pages for every segment and domain, each with its own link-preview card
- `CNAME`, `robots.txt`, `sitemap.xml`, `404.html` - hosting plumbing
- `scripts/genome_watch.py` + `.github/workflows/genome-watch.yml` - the monthly watch agent

## Genome Watch agent
A scheduled GitHub Action (1st of each month, or run manually from the Actions tab).

## License
© 2026 Battery Industry Genome™. All rights reserved - see `LICENSE.txt`.
Contact: [@ssripad1](https://x.com/ssripad1) · [linkedin.com/in/ssripad](https://www.linkedin.com/in/ssripad/)
