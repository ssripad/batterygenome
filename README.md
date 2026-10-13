# Battery Industry Genome™

Live at **[batterygenome.net](https://batterygenome.net)**. Edition 2026-10-10 (v1.26).

16 domains · 171 application segments · ~$365B of 2025 battery demand, mapped by
application, market size (audited, with ranges), an 8-axis requirement fingerprint,
price band, ranked top-5 suppliers, and a reference cell design per segment,
rendered in 3D and exportable as STL and DXF.
One self-contained HTML file - no build, no dependencies.

## Genome Watch agent
A scheduled GitHub Action (1st of each month, or run manually from the Actions tab).

## License
One license file, [`LICENSE`](LICENSE): the site code and scripts are GPL-3.0; the dataset and content
(taxonomy, estimates, cell designs, text, images) are © 2026 Shashank Sripad, all rights reserved.
Contact: [@ssripad1](https://x.com/ssripad1) · [linkedin.com/in/ssripad](https://www.linkedin.com/in/ssripad/)

## Companies page
Click "Battery stocks" in the ticker to open `/stocks/`. It lists the ticker companies by market cap in USD and shows
the latest full-year battery volume each company reports (GWh or MWh), with the basis, the year and a source link.
Third-party figures (for example SNE Research EV installations) are marked. It can be filtered by group and country,
sorted by any column, and grouped by country. Market caps come from `data/prices.json` (`mc`, USD, refreshed once a
day, or on every manual run of the workflow). Countries and volumes live in `index.html` under `meta.tickers`
(`cc`, `v`).
