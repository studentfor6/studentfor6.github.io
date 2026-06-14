# Word to Jekyll Blog Post Converter

Convert Word `.docx` files directly to Jekyll blog posts with embedded images, tables, and Tailwind styling.

## Installation

Install the required Python package:

```bash
pip install mammoth
```

## Usage

### Basic Conversion

```bash
python docx_to_post.py "My Blog Post.docx" "My Blog Post Title" "2026-06-15"
```

This will create:
- **Post:** `_posts/2026-06-15-my-blog-post-title.md`
- **Images:** `assets/images/my-blog-post-title/*.png|jpg|jpeg|gif`

### With Custom Repo Path

If running from outside the repo root:

```bash
python docx_to_post.py "document.docx" "Title" "2026-06-15" --repo /path/to/studentfor6.github.io
```

## What It Does

1. **Converts Word to HTML** — Uses Mammoth to preserve structure (headings, lists, tables).
2. **Extracts Images** — Pulls all images from the DOCX and saves to `assets/images/<post-slug>/`.
3. **Adds Tailwind Classes** — Styles headings, paragraphs, lists, and tables to match your site theme (blue header, responsive tables).
4. **Generates Jekyll Frontmatter** — Adds post metadata (layout, date, title).
5. **Outputs Markdown** — Ready to commit to `_posts/`.

## Word to Jekyll Mapping

| Word Element | Jekyll Output |
|---|---|
| Heading 1 | `<h1>` with `text-3xl font-bold` |
| Heading 2 | `<h2>` with `text-2xl font-semibold` |
| Heading 3 | `<h3>` with `text-xl font-semibold` |
| Normal text | `<p>` with `text-base text-slate-700` |
| Bullet list | `<ul>` with `list-disc` |
| Numbered list | `<ol>` with `list-decimal` |
| Table | Scrollable `<table>` with blue header (`#0f4d8a`) |
| Inline images | Extracted to `assets/images/<slug>/` and linked |

## Post-Conversion Review

After conversion, always:

1. **Edit the frontmatter** — Update `description`, add `tags`, adjust `date` if needed:

```yaml
---
layout: post
title: "My Blog Post Title"
date: 2026-06-15
description: "A brief summary of your post"
tags: [tag1, tag2]
---
```

2. **Review the markdown** — Open the file and check for:
   - Proper heading hierarchy
   - Table formatting
   - Image references

3. **Add to git and push**:

```bash
git add _posts/2026-06-15-my-blog-post-title.md assets/images/my-blog-post-title/
git commit -m "Post: My Blog Post Title (auto-converted from Word)"
git push
```

## Limitations

- Complex Word features (SmartArt, advanced styling) may not convert perfectly.
- Exact pixel-perfect matching to Word is not guaranteed (web fonts differ).
- Some Word formatting (e.g., custom colors) is simplified to Tailwind defaults.

## Troubleshooting

**"mammoth not installed"** — Run: `pip install mammoth`

**"File not found"** — Check the path to your DOCX file is correct.

**"Invalid date format"** — Use `YYYY-MM-DD` format, e.g., `2026-06-15`.

**Images not extracted** — Some DOCX files use different media storage. Try opening the DOCX in Word, resaving, and trying again.

## For Developers

The script is in `tools/docx_to_post.py`. To customize Tailwind classes or add new post-processing rules, edit the `post_process_html()` function.
