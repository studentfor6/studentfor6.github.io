#!/usr/bin/env python3
"""
Post formatter to:
1. Center-align text in table headers (blue boxes)
2. Ensure text in blue boxes is white and visible
3. Move footnotes below their respective tables
4. Add Disclaimer and comments section
"""

import re
from pathlib import Path


def fix_blue_boxes(html):
    """Add center alignment and fix text color in blue table headers."""
    # Fix table headers: add text-center and ensure white text is visible
    # The issue is nested <p> tags with slate-700 color override the white text
    
    # Find all th elements with bg-[#0f4d8a]
    pattern = r'<th class="bg-\[#0f4d8a\] text-white border-b border-slate-200 px-6 py-3 text-left font-semibold align-middle"><p class="text-base text-slate-700 mb-3 leading-relaxed"><strong>([^<]+)</strong></p></th>'
    
    replacement = r'<th class="bg-[#0f4d8a] text-white border-b border-slate-200 px-6 py-3 text-center font-semibold align-middle"><p class="text-base text-white mb-3 leading-relaxed"><strong>\1</strong></p></th>'
    
    html = re.sub(pattern, replacement, html)
    return html


def extract_footnotes(html):
    """Extract footnote definitions and their corresponding references."""
    # Find all footnote references and their definitions
    footnote_pattern = r'<ol class="list-decimal pl-6 space-y-2 text-base text-slate-700 mb-3">\s*(<li id="footnote-\d+">.+?</li>)\s*</ol>'
    
    match = re.search(footnote_pattern, html, re.DOTALL)
    footnotes_html = ""
    
    if match:
        footnotes_html = match.group(1)
        # Remove from original position
        html = html[:match.start()] + html[match.end():]
    
    return html, footnotes_html


def find_table_footnotes(html, table_index):
    """Find footnotes referenced within a specific table."""
    # Split by tables
    tables = re.findall(r'<div class="overflow-x-auto[^>]*>.*?</div>', html, re.DOTALL)
    
    if table_index >= len(tables):
        return []
    
    table = tables[table_index]
    
    # Find all footnote references in this table
    footnote_refs = re.findall(r'footnote-(\d+)', table)
    return list(set(footnote_refs))  # Remove duplicates


def reorganize_footnotes(html, footnotes_html):
    """Move footnotes below their respective tables and add disclaimer."""
    # Find all tables
    tables = list(re.finditer(r'<div class="overflow-x-auto[^>]*>.*?</table>\s*</div>', html, re.DOTALL))
    
    if not tables:
        return html
    
    # Process tables in reverse order to avoid index shifts
    for i in range(len(tables) - 1, -1, -1):
        table = tables[i]
        table_text = html[table.start():table.end()]
        
        # Find footnote numbers referenced in this table
        footnote_nums = re.findall(r'footnote-(\d+)', table_text)
        
        if footnote_nums:
            # Extract these specific footnotes
            footnote_nums = list(set(footnote_nums))
            
            table_footnotes = ""
            for num in sorted(footnote_nums, key=int):
                # Find the specific footnote definition
                pattern = rf'<li id="footnote-{num}">.*?</li>'
                match = re.search(pattern, footnotes_html, re.DOTALL)
                if match:
                    table_footnotes += match.group(0)
            
            if table_footnotes:
                # Wrap in ol tags
                footnotes_section = f'<ol class="list-decimal pl-6 space-y-2 text-base text-slate-700 mb-3">\n{table_footnotes}\n</ol>'
                
                # Insert after the table
                insert_pos = table.end()
                html = html[:insert_pos] + "\n" + footnotes_section + "\n" + html[insert_pos:]
    
    return html


def add_disclaimer_and_comments(html):
    """Add Disclaimer and comments section before closing div."""
    disclaimer_html = '''
<hr class="my-8 border-slate-300">
<p class="text-base text-slate-700 mb-3 leading-relaxed"><strong>Disclaimer</strong></p>
<p class="text-sm text-slate-600 mb-6 leading-relaxed">This information is provided for educational purposes only and should not be considered as legal or regulatory advice. Always consult with qualified regulatory professionals for specific guidance.</p>

<hr class="my-8 border-slate-300">
<h3 class="text-lg font-semibold text-[#0f4d8a] mb-4">Comments</h3>
<div id="comments-section" class="bg-slate-50 p-6 rounded-lg border border-slate-200">
  <form id="comment-form" class="space-y-4">
    <div>
      <label for="commenter-name" class="block text-base font-medium text-slate-700 mb-2">Name</label>
      <input type="text" id="commenter-name" name="name" class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0f4d8a]" required>
    </div>
    <div>
      <label for="commenter-email" class="block text-base font-medium text-slate-700 mb-2">Email</label>
      <input type="email" id="commenter-email" name="email" class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0f4d8a]" required>
    </div>
    <div>
      <label for="commenter-comment" class="block text-base font-medium text-slate-700 mb-2">Your Comment</label>
      <textarea id="commenter-comment" name="comment" rows="4" class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0f4d8a]" required></textarea>
    </div>
    <button type="submit" class="px-6 py-2 bg-[#0f4d8a] text-white font-semibold rounded-lg hover:bg-[#0a3a5f] transition">Submit Comment</button>
  </form>
  <div id="comments-list" class="mt-6 space-y-4">
    <p class="text-slate-600 text-sm">Comments will appear here...</p>
  </div>
</div>
'''
    
    # Insert before closing div
    if html.endswith('</div>'):
        html = html[:-6] + disclaimer_html + '\n</div>'
    else:
        html = html.rstrip() + '\n' + disclaimer_html
    
    return html


def format_post(file_path):
    """Main function to format the blog post."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split frontmatter and body
    parts = content.split('---', 2)
    if len(parts) < 3:
        print("Error: Invalid markdown format")
        return
    
    frontmatter = parts[0] + '---' + parts[1] + '---'
    body = parts[2]
    
    # Apply transformations
    print("1. Fixing blue boxes (center align + white text)...")
    body = fix_blue_boxes(body)
    
    print("2. Extracting footnotes...")
    body, footnotes_html = extract_footnotes(body)
    
    print("3. Reorganizing footnotes below tables...")
    body = reorganize_footnotes(body, footnotes_html)
    
    print("4. Adding disclaimer and comments section...")
    body = add_disclaimer_and_comments(body)
    
    # Recombine
    formatted_content = frontmatter + body
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(formatted_content)
    
    print(f"✓ Post formatted successfully: {file_path}")


if __name__ == '__main__':
    post_path = Path(r"c:\Users\vivec\studentfor6.github.io\_posts\2026-06-14-mhra-irp-auto-converted.md")
    if post_path.exists():
        format_post(post_path)
    else:
        print(f"Error: File not found: {post_path}")
