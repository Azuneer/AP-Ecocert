import html
import posixpath
import re

import markdown as md


def on_page_markdown(markdown, page, config, files):
    path = page.file.src_uri
    if path.endswith('index.md') or not path.startswith(('situations/', 'missions/', 'documentation/', 'ressources/table')):
        return markdown
    lines = markdown.splitlines()
    if not lines or not lines[0].startswith('# '):
        return markdown
    cub = 'logo_cub' in str(config['theme'].get('logo', ''))
    project = 'CUB' if cub else 'Ecocert'
    logo = 'assets/logo_cub.png' if cub else 'assets/ecocertlogo.png'
    logo = posixpath.relpath(logo, posixpath.dirname(path))
    metadata = []
    end = 1
    for i, line in enumerate(lines[1:], 1):
        if not line.strip():
            end = i + 1
            continue
        if re.match(r'!\[.*\]\([^)]*(?:logo_cub|ecocertlogo)[^)]*\)', line):
            end = i + 1
            continue
        clean = re.sub(r'^>\s*', '', line)
        clean = re.sub(r'^:[\w-]+:\s*', '', clean)
        match = re.match(r'(?:\*\*)?(Fiche rédigée par|Formation|Établissement|Date de recette|Date|Groupe|Version du document|Version|Contexte)(?:\*\*)?\s*:\s*(.+)', clean)
        if not match:
            break
        label, value = match.groups()
        value = md.markdown(value.strip())
        value = re.sub(r'^<p>|</p>$', '', value)
        metadata.append(f'<div class="fiche-field"><dt>{html.escape(label)}</dt><dd>{value}</dd></div>')
        end = i + 1
    fields = '<dl class="fiche-metadata">' + ''.join(metadata) + '</dl>' if metadata else ''
    header = (
        '<div class="fiche-header" markdown="1">\n'
        '<div class="fiche-identity" markdown="1">\n\n'
        f'![Logo {project}]({logo}){{ .fiche-logo width="150" }}\n\n'
        f'<span class="fiche-project">{project} · BTS SIO SISR</span>\n\n</div>\n'
        f'{fields}\n</div>'
    )
    body = '\n'.join(lines[end:]).lstrip()
    if body.startswith('---\n'):
        body = body[4:].lstrip()
    return lines[0] + '\n\n' + header + '\n\n' + body + '\n'
