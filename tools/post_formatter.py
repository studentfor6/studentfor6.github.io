

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
    # Find all footnote <li> definitions across the document
    li_pattern = re.compile(r'<li\s+id="footnote-\d+">.*?</li>', re.DOTALL)
    li_matches = li_pattern.findall(html)
    footnotes_html = "".join(li_matches)

    # Remove all matched <li> blocks and any surrounding empty <ol> wrappers
    if li_matches:
        html = li_pattern.sub('', html)
        # remove empty ol blocks left behind
        html = re.sub(r'<ol[^>]*>\s*</ol>', '', html)

    return html, footnotes_html



# def find_table_footnotes(html, table_index):
#     """Find footnotes referenced within a specific table."""
#     # Split by tables
#     tables = re.findall(r'<div class="overflow-x-auto[^>]*>.*?</div>', html, re.DOTALL)
    
#     if table_index >= len(tables):
#         return []
    
#     table = tables[table_index]
    
#     # Find all footnote references in this table
#     footnote_refs = re.findall(r'footnote-(\d+)', table)
#     return list(set(footnote_refs))  # Remove duplicates


# def reorganize_footnotes(html, footnotes_html):
#     """Move footnotes below their respective tables and add disclaimer."""
#     # Find all tables
#     tables = list(re.finditer(r'<div class="overflow-x-auto[^>]*>.*?</table>\s*</div>', html, re.DOTALL))
    
#     if not tables:
#         return html

#     # Process tables in reverse order to avoid index shifts
#     used_originals = set()
#     for i in range(len(tables) - 1, -1, -1):
#         table = tables[i]
#         table_text = html[table.start():table.end()]

#         # Find footnote references in this table in appearance order
#         ref_pattern = re.compile(r'<a[^>]*href="#footnote-(\d+)"[^>]*id="footnote-ref-(\d+)"[^>]*>\[.*?\]</a>')
#         refs = ref_pattern.findall(table_text)
#         if not refs:
#             continue

#         # Build unique ordered list of original footnote numbers as they appear
#         ordered_nums = []
#         for orig, _ in refs:
#             if orig not in ordered_nums:
#                 ordered_nums.append(orig)

#         # Map original numbers to new sequential numbers (per-table)
#         # Use a prefixed id to keep anchor ids unique across the page, e.g. '2-1'
#         mapping = {}
#         for idx, orig in enumerate(ordered_nums):
#             label = str(idx + 1)
#             prefixed = f"{i+1}-{label}"
#             mapping[orig] = (label, prefixed)

def extract_footnotes(html):
    """
    Extract all footnote <li> blocks and remove them from the HTML.
    Keep original numbering exactly as Mammoth produced.
    """
    li_pattern = re.compile(r'<li\s+id="footnote-\d+">.*?</li>', re.DOTALL)
    matches = li_pattern.findall(html)

    # Remove footnotes from body
    html = li_pattern.sub('', html)

    # Remove empty <ol> left behind
    html = re.sub(r'<ol[^>]*>\s*</ol>', '', html)

    # Combine into a single ordered list
    if matches:
        footnotes_html = (
            '<ol class="list-decimal pl-6 space-y-2 text-sm text-slate-600 mb-6">\n'
            + "\n".join(matches)
            + "\n</ol>"
        )
    else:
        footnotes_html = ""

    return html, footnotes_html

def insert_footnotes_at_end(html, footnotes_html):
    """
    Append all footnotes at the end of the post (before disclaimer/comments).
    No renumbering, no table grouping.
    """
    if not footnotes_html:
        return html

    # Insert before final </div> of prose container
    if html.rstrip().endswith("</div>"):
        html = html.rstrip()[:-6] + footnotes_html + "\n</div>"
    else:
        html = html + "\n" + footnotes_html

    return html


    #     # Update references inside the table_html to new numbers and unique ids
    #     def repl_ref(match):
    #         orig = match.group(1)
    #         label, pref = mapping.get(orig, (orig, orig))
    #         new_href = f'href="#footnote-{pref}"'
    #         new_id = f'id="footnote-ref-{pref}"'
    #         return match.group(0).replace(f'href="#footnote-{orig}"', new_href).replace(f'id="footnote-ref-{orig}"', new_id).replace(f'[{orig}]', f'[{label}]')

    #     table_text_updated = ref_pattern.sub(repl_ref, table_text)

    #     # Extract and renumber corresponding footnote definitions
    #     table_footnotes = ""
    #     for orig in ordered_nums:
    #         li_pattern = re.compile(rf'(<li\s+id="footnote-{orig}">.*?</li>)', re.DOTALL)
    #         m = li_pattern.search(footnotes_html)
    #         if m:
    #             li_html = m.group(1)
    #             label, pref = mapping[orig]
    #             # Update li id and backlink hrefs inside the li to use prefixed ids
    #             li_html = re.sub(rf'id="footnote-{orig}"', f'id="footnote-{pref}"', li_html)
    #             li_html = re.sub(rf'href="#footnote-ref-{orig}"', f'href="#footnote-ref-{pref}"', li_html)
    #             # Also update any display of the reference number in the li if present
    #             li_html = re.sub(rf'\[\s*{orig}\s*\]', f'[{label}]', li_html)
    #             # Reduce footnote paragraph text size and colour for clarity
    #             li_html = re.sub(r'text-base text-slate-700', 'text-sm text-slate-600', li_html)
    #             table_footnotes += li_html
    #             used_originals.add(orig)

    #     if table_footnotes:
    #         # Wrap in ol tags with smaller footnote text
    #         footnotes_section = f'<ol class="list-decimal pl-6 space-y-2 text-sm text-slate-600 mb-3">\n{table_footnotes}\n</ol>'

    #         # Replace the original table with the updated one
    #         html = html[:table.start()] + table_text_updated + html[table.end():]

    #         # Insert the footnotes_section after the updated table
    #         insert_pos = table.start() + len(table_text_updated)
    #         html = html[:insert_pos] + "\n" + footnotes_section + "\n" + html[insert_pos:]

    # # After placing table-specific footnotes, append any remaining (non-table) footnotes
    # remaining_footnotes = ""
    # li_pattern_all = re.compile(r'<li\s+id="footnote-(\d+)">(.*?)</li>', re.DOTALL)
    # for m in li_pattern_all.finditer(footnotes_html):
    #     orig = m.group(1)
    #     li_html = m.group(0)
    #     if orig in used_originals:
    #         continue
    #     # ensure small muted styling
    #     li_html = re.sub(r'text-base text-slate-700', 'text-sm text-slate-600', li_html)
    #     remaining_footnotes += li_html

    # if remaining_footnotes:
    #     global_section = f'<ol class="list-decimal pl-6 space-y-2 text-sm text-slate-600 mb-3">\n{remaining_footnotes}\n</ol>'
    #     # Append near end before disclaimer/comments if present
    #     # place before the last closing </div>
    #     if html.rstrip().endswith('</div>'):
    #         html = html.rstrip()[:-6] + global_section + '\n</div>'
    #     else:
    #         html = html + '\n' + global_section

    # return html
    


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
            <label for="commenter-email" class="block text-base font-medium text-slate-700 mb-2">Email (optional)</label>
            <input type="email" id="commenter-email" name="email" class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0f4d8a]">
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
    
    # Remove any previously inserted disclaimer/comments blocks to avoid duplicates
    html = re.sub(r'<hr class="my-8 border-slate-300">[\s\S]*?<div id="comments-section"[\s\S]*?</div>\s*</div>', '', html)

    # Insert before closing div
    if html.rstrip().endswith('</div>'):
        html = html.rstrip()[:-6] + disclaimer_html + '\n</div>'
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
    # body = reorganize_footnotes(body, footnotes_html)
    body = insert_footnotes_at_end(body, footnotes_html)

    
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
