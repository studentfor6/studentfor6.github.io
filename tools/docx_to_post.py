#!/usr/bin/env python3
"""
Convert Word .docx files to Jekyll blog posts with images and Tailwind styling.

Usage:
  python docx_to_post.py "path/to/document.docx" "Post Title" "2026-06-15"

Output:
  - Jekyll post: _posts/2026-06-15-post-title.md
  - Images: assets/images/post-title/image1.png, image2.jpg, etc.
"""

import sys
import os
import re
import argparse
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
import shutil

try:
    import mammoth
except ImportError:
    print("ERROR: mammoth not installed. Install it with:")
    print("  pip install mammoth")
    sys.exit(1)


def slugify(title):
    """Convert title to URL-safe slug."""
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def extract_images_from_docx(docx_path, slug, repo_root):
    """Extract images from DOCX and return mapping of old_src -> new_src."""
    image_map = {}
    image_dir = Path(repo_root) / "assets" / "images" / slug
    image_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        from zipfile import ZipFile
        import xml.etree.ElementTree as ET
        
        with ZipFile(docx_path) as docx_zip:
            # Extract media files
            for item in docx_zip.namelist():
                if item.startswith('word/media/'):
                    # e.g., word/media/image1.png
                    filename = Path(item).name
                    with docx_zip.open(item) as src:
                        dest_path = image_dir / filename
                        with open(dest_path, 'wb') as dst:
                            dst.write(src.read())
                    
                    # Map internal reference to web path
                    old_ref = f"word/media/{filename}"
                    new_ref = f"/assets/images/{slug}/{filename}"
                    image_map[old_ref] = new_ref
    except Exception as e:
        print(f"WARNING: Could not extract images: {e}")
    
    return image_map


def post_process_html(html, image_map, slug):
    """
    Post-process Mammoth HTML to add Tailwind classes and rewrite image paths.
    Converts Word semantics to Jekyll-friendly HTML with styling.
    """
    from html.parser import HTMLParser
    from io import StringIO
    
    # Rewrite image paths
    for old_src, new_src in image_map.items():
        # Replace both absolute and relative paths
        html = html.replace(f'src="{old_src}"', f'src="{new_src}"')
        html = html.replace(f"src='{old_src}'", f"src='{new_src}'")
    
    # Add Tailwind classes to key elements
    # Headings
    html = re.sub(r'<h1>', '<h1 class="text-3xl font-bold text-slate-900 mb-4">', html)
    html = re.sub(r'<h2>', '<h2 class="text-2xl font-semibold text-slate-900 mb-3 mt-6">', html)
    html = re.sub(r'<h3>', '<h3 class="text-xl font-semibold text-slate-900 mb-2 mt-4">', html)
    html = re.sub(r'<h4>', '<h4 class="text-lg font-semibold text-slate-900 mb-2">', html)
    
    # Paragraphs
    html = re.sub(r'<p>', '<p class="text-base text-slate-700 mb-3 leading-relaxed">', html)
    
    # Lists
    html = re.sub(r'<ul>', '<ul class="list-disc pl-6 space-y-2 text-base text-slate-700 mb-3">', html)
    html = re.sub(r'<ol>', '<ol class="list-decimal pl-6 space-y-2 text-base text-slate-700 mb-3">', html)
    
    # Tables - add scrollable wrapper and Tailwind styling
    html = re.sub(
        r'<table>',
        '<div class="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm my-4">'
        '<table class="min-w-full border-collapse text-sm">',
        html
    )
    html = re.sub(r'</table>', '</table></div>', html)
    
    # Table headers
    html = re.sub(
        r'<th>',
        '<th class="bg-[#0f4d8a] text-white border-b border-slate-200 px-6 py-3 text-left font-semibold align-middle">',
        html
    )
    
    # Table cells
    html = re.sub(
        r'<td>',
        '<td class="border-b border-slate-200 px-6 py-3 text-slate-700 align-top">',
        html
    )
    
    # Wrap content in prose container for consistency
    html = f'<div class="prose max-w-full">\n{html}\n</div>'
    
    return html


def create_jekyll_post(docx_path, title, date_str, repo_root):
    """
    Convert DOCX to Jekyll post with images and frontmatter.
    
    Args:
        docx_path: Path to .docx file
        title: Post title (string)
        date_str: Date in YYYY-MM-DD format
        repo_root: Path to Jekyll repo root
    
    Returns:
        Path to created post file
    """
    docx_path = Path(docx_path)
    if not docx_path.exists():
        print(f"ERROR: File not found: {docx_path}")
        sys.exit(1)
    
    repo_root = Path(repo_root)
    posts_dir = repo_root / "_posts"
    posts_dir.mkdir(exist_ok=True)
    
    # Parse date
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print(f"ERROR: Invalid date format. Use YYYY-MM-DD (got: {date_str})")
        sys.exit(1)
    
    slug = slugify(title)
    
    # Step 1: Convert DOCX to HTML using Mammoth
    print(f"Converting {docx_path.name} to HTML...")
    with open(docx_path, 'rb') as f:
        result = mammoth.convert_to_html(f)
        html = result.value
    
    # Step 2: Extract images
    print("Extracting images...")
    image_map = extract_images_from_docx(docx_path, slug, repo_root)
    
    # Step 3: Post-process HTML
    print("Post-processing HTML with Tailwind classes...")
    html = post_process_html(html, image_map, slug)
    
    # Step 4: Create Jekyll frontmatter
    frontmatter = f"""---
layout: post
title: "{title}"
date: {date_str}
description: "Auto-converted from Word document"
---

"""
    
    # Step 5: Write post file
    post_filename = f"{date_str}-{slug}.md"
    post_path = posts_dir / post_filename
    
    with open(post_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
        f.write(html)
    
    print(f"✓ Post created: {post_path}")
    if image_map:
        print(f"✓ Images saved to: assets/images/{slug}/")
    print(f"\nNext steps:")
    print(f"  1. Review the post: {post_path}")
    print(f"  2. Adjust frontmatter (description, tags, etc.) as needed")
    print(f"  3. Add to git: git add {post_path}")
    print(f"  4. Commit and push")
    
    return post_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert Word documents to Jekyll blog posts",
        epilog="Example: python docx_to_post.py 'document.docx' 'My Post Title' '2026-06-15'"
    )
    parser.add_argument('docx', help='Path to .docx file')
    parser.add_argument('title', help='Post title')
    parser.add_argument('date', help='Post date (YYYY-MM-DD)')
    parser.add_argument('--repo', default='.', help='Path to Jekyll repo root (default: current dir)')
    
    args = parser.parse_args()
    
    try:
        create_jekyll_post(args.docx, args.title, args.date, args.repo)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
