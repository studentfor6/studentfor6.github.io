# studentfor6.github.io
Regulatory Consultancy Website

Here's the structure
blog.html — Jekyll page template for the Insights blog; loops site.posts and renders post title, date, and content with Tailwind classes.

index.md — Site homepage (Jekyll) with hero, navigation, services grid, feature grid, blog CTA, contact section, and inline animation CSS.

index2.md — Alternate/sandbox homepage variant with a colorful hero, service cards, feature grid, CTA, and animation utilities.

MHRA International Recognition Procedure.docx — Word document describing the MHRA IRP: purpose, reference regulators, evolution timeline, recognition routes (A/B), submission guidance, post‑authorisation notes, and sources.

README.md — Repository readme with a short site title/logo snippet.

docx_to_post.py — Python converter script (uses mammoth) that converts .docx to a Jekyll post, extracts images to assets/images/, post-processes HTML with Tailwind classes, and writes _posts/YYYY-MM-DD-...md.

post_formatter.py (also provided as #!_usr_bin_env python3.txt) — Python post-processor that:

fixes blue table headers (centers text, ensures white text),

extracts/moves footnote <li> blocks,

appends a Disclaimer and Comments section,

supports dry-run and --inplace with backup behavior; uses regex-based transformations.

_posts/2026-06-14-mhra-irp-auto-converted.md — Auto-converted Jekyll post generated from the DOCX; contains Mammoth-produced HTML (headings, tables, lists), footnotes moved to the end, and a disclaimer block.

_posts/2026-06-20-test1.md — Simple test post (Markdown) used for verification.

assets/css/style.css (your CSS file in assets/css/) — Site stylesheet with :root variables, hero styles, layout cards, .prose rules, and table/typography refinements (the file you pasted).

_layouts/default.html — Site layout: includes Tailwind CDN, links /assets/css/style.css, renders {{ content }}, and contains the site footer.

tools/ (folder) — contains the Python utilities (docx_to_post.py, post_formatter.py) you provided; you confirmed the .py files live here.

<!-- Logo + Brand -->
    <div class="flex items-center gap-3">
      <img src="/assets/images/logo.png" class="w-12 h-12" alt="Logo">
      <span class="text-xl font-semibold text-gray-800">A‑Star Regulatory Solutions</span>
    </div>
