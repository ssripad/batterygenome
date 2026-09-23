# Battery Industry Genome™

Live at **[batterygenome.net](https://batterygenome.net)**.

16 domains · 170 application segments · ~$365B of 2025 battery demand, mapped by
application, market size (audited, with ranges), an 8-axis requirement fingerprint,
price band, ranked top-5 suppliers, and a reference cell design per segment.
One self-contained HTML file - no build, no dependencies.

## Structure
- `index.html` - the entire genome (app + embedded data)
- `og-image.png`, `apple-touch-icon.png` - social/link previews
- `CNAME`, `robots.txt`, `sitemap.xml`, `404.html` - hosting plumbing
- `scripts/genome_watch.py` + `.github/workflows/genome-watch.yml` - the monthly watch agent

## Genome Watch agent
A scheduled GitHub Action (1st of each month, or run manually from the Actions tab).
It parses every supplier out of `index.html`, uses Claude with web search to look for
bankruptcies, insolvency processes, acquisitions and renames, checks the market anchors
(BNEF pack prices, IEA volumes, the 12 largest segments) for >20% drift, and files the
findings as a `genome-watch` issue. It never edits data - flags only, a human merges.

Setup: repo Settings → Secrets and variables → Actions → new secret
`ANTHROPIC_API_KEY` (an Anthropic API key). Typical run: a few dollars of API usage.

## License
© 2026 Battery Industry Genome™. All rights reserved - see `LICENSE.txt`.
Contact: [@ssripad1](https://x.com/ssripad1) · [linkedin.com/in/ssripad](https://www.linkedin.com/in/ssripad/)
