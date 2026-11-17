#!/usr/bin/env python3
"""Rebuild the corrected GRETIL files.

    python3 build.py            # 1. download  2. read corrections.json  3. write corrected/*.htm
    python3 build.py --verify   # only check that the downloaded files are the ones corrections.json expects

Needs Python 3.9+ and git. No other dependency. See README.md.
"""
import datetime
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
MIRROR_DIR = os.path.join(HERE, 'mirror')
OUT_DIR = os.path.join(HERE, 'corrected')
BASE = os.path.join(MIRROR_DIR, 'gretil.sub.uni-goettingen.de', 'gretil', '2_pali')
DATA = json.load(open(os.path.join(HERE, 'corrections.json'), encoding='utf-8'))

#: volume -> files (without extension), below `gretil/2_pali/` in the mirror
FILES = DATA['files']


# 1. download -----------------------------------------------------------------------------

def download():
    """The pinned commit of the mirror, only the Pāli folders (about 100 MB)."""
    def git(*a):
        subprocess.run(['git', '-C', MIRROR_DIR, *a], check=True)
    if not os.path.isdir(os.path.join(MIRROR_DIR, '.git')):
        os.makedirs(MIRROR_DIR, exist_ok=True)
        subprocess.run(['git', 'init', '-q', MIRROR_DIR], check=True)
        git('remote', 'add', 'origin', DATA['mirror'])
    git('fetch', '-q', '--depth', '1', '--filter=blob:none', 'origin', DATA['commit'])
    git('sparse-checkout', 'set', '--cone', 'gretil.sub.uni-goettingen.de/gretil/2_pali/1_tipit',
        'gretil.sub.uni-goettingen.de/gretil/2_pali/2_parcan')
    git('checkout', '-q', 'FETCH_HEAD')


def verify():
    """The input is exactly what the corrections were made on."""
    bad = []
    for rel, digest in DATA['sources'].items():
        path = os.path.join(BASE, rel)
        if not os.path.exists(path) or hashlib.sha256(open(path, 'rb').read()).hexdigest() != digest:
            bad.append(rel)
    if bad:
        sys.exit('These files differ from the ones the corrections were made on:\n  ' + '\n  '.join(bad))


# 2. read GRETIL's pages (the conventions the corrections are written in) ------------------

_BR = re.compile(r'<br\s*/?>')
_PAGE = re.compile(r'<b>\[page (?:<span class="red"><sup>)?(\d+)(?:</sup></span>)?\]</b><BR>\n')
_NOTES = re.compile(r'<span class="red">-{10,}<BR>\n?(.*?)</span>(?:<BR>)?\n?', re.S)
_HEAD = re.compile(r'<i>(.*?)</i><BR>\n', re.S)
_CALL = re.compile(r'<span class="red"><sup>(.*?)</sup></span>')
_LABEL = re.compile(r'<[^>]+>')
_SN_MARKER = re.compile(r'SN_[0-9.,()]+\s?|Sn_[IVX]+,[0-9.]+\s?'
                        r'|Thī?_\*?[0-9.,]+\s?|Dhp_[0-9.,()-]+\s?'
                        r'|Vv_[IVX]+,[0-9]+\[=[0-9]+\]\.[0-9-]+\s?'
                        r'|Ap(?:Tha|Thi|Bud|Pac)_[0-9.,]+\s?'
                        r'|Nidd_I\.[0-9]+:[0-9]+\s?'
                        r'|Cp_[IVX]+,[0-9.]+\s?|Bv_[0-9]+\.[0-9]+\s?'
                        r'|Paṭis_[IVX]+,[IVX]+\.[0-9.]+:\s?'
                        r'|Dhātuk_[IVX]* ?\.[0-9]+(?:[,-][0-9]+)?\s?')
_AS_IN = re.compile(r'\b(?:As in|The same as) No\. \d+(?:,[0-9-]+)?')
_LETTER = r'[^\W\d_]'
_VOWEL = 'aāiīuūeoAĀIĪUŪEO'
_ELISION = re.compile(r"(?<=[^\W\d_" + _VOWEL + r"ṃ])';(?=[ \t]*\n?[ \t]*-?[" + _VOWEL + '])')
_CONTROL = re.compile(r'[\x00-\x08\x0b-\x1f\x7f]')
_DASH = re.compile(r'^_{5,}\s*$', re.M)
_ABBREVIATE = (
    (re.compile(r'(?<=' + _LETTER + r')-(?=[ \t]+(?!--)\S)'), 'º'),
    (re.compile(r'(?<![^\s])-(?=' + _LETTER + ')'), 'º'),
    (re.compile(r'(?m)^([ \t]*)-(?=[ \t]+' + _LETTER + ')'), r'\1º'),
    (re.compile(r'(?<=' + _LETTER + r')-(?=[ \t]*\n[ \t]*[\[º(])'), 'º'),
)


def plain(t):
    return html.unescape(_LABEL.sub('', t.replace('<BR>\n', '\n').replace('<BR>', '\n')))


def body(chunk, abbreviate=True):
    """The body of a GRETIL page: note calls as digits, GRETIL's markers removed, the
    abbreviation sign `º` and the elision apostrophe `’` rebuilt from GRETIL's hyphen and `';`."""
    c = _CALL.sub(r'\1', chunk)
    c = _SN_MARKER.sub('', c)
    c = _AS_IN.sub('. . .', c)
    c = plain(c).replace('||', '║')
    c = _ELISION.sub("'", c).replace("';", '’')
    c = _DASH.sub('', c)
    c = re.sub(r'ḥ(?=[ \t]*(?:\n|$))', '', c)
    c = re.sub(r"(['’]\s+)-(?=" + _LETTER + ')', '\\1\x00', c)
    if abbreviate:
        for pattern, rep in _ABBREVIATE:
            c = pattern.sub(rep, c)
    c = c.replace('\x00', '-')
    return _CONTROL.sub('', c)


def parts(source, abbreviate=True):
    """`{page: (running head, body, footnotes)}` of a whole GRETIL file."""
    z = _PAGE.split(source)
    out = {}
    for i in range(1, len(z), 2):
        c = z[i + 1]
        notes = '\n'.join(plain(n).strip('\n') for n in _NOTES.findall(c))
        c = _NOTES.sub('', c)
        m = _HEAD.match(c)
        head = plain(m.group(1)).strip() if m else ''
        if m:
            c = c[m.end():]
        out[int(z[i])] = (head, body(c, abbreviate), notes)
    return out


# 3. apply the corrections, write the pages -------------------------------------------------

CORRECTIONS = {}
for c in DATA['corrections']:
    CORRECTIONS.setdefault((c['volume'], c['page']), []).append(c)


def _tokens(t):
    return re.split(r'(\s+)', t)


def _trim(old, new):
    """For corrections generated from a corrected file, only the words that change are the correction."""
    a, b = _tokens(old), _tokens(new)
    i = 0
    while i < min(len(a), len(b)) and a[i] == b[i]:
        i += 1
    j = 0
    while j < min(len(a), len(b)) - i and a[-1 - j] == b[-1 - j]:
        j += 1
    return ''.join(a[:i]), ''.join(a[i:len(a) - j]), ''.join(b[i:len(b) - j]), ''.join(a[len(a) - j:])


def apply(volume, n, part, text):
    """The text with its corrections, and for every character the corrections that wrote it."""
    t, who = text, [()] * len(text)
    for c in CORRECTIONS.get((volume, n), []):
        if c.get('part', 'text') != part:
            continue
        old, new = c['gretil'], c['book']
        if t.count(old) != c['times']:
            sys.exit(f'{volume} p. {n}: {old!r} is there {t.count(old)} times, the correction says {c["times"]}')
        keep_l, mid_old, mid_new, keep_r = _trim(old, new) if c.get('ctx') else ('', old, new, '')
        out, owners, i = [], [], 0
        while True:
            j = t.find(old, i)
            if j < 0:
                break
            out.append(t[i:j])
            owners += who[i:j]
            out.append(keep_l)
            owners += who[j:j + len(keep_l)]
            out.append(mid_new)
            owners += [tuple(x for w in who[j + len(keep_l):j + len(keep_l) + len(mid_old)] for x in w) + (c,)] * len(mid_new)
            out.append(keep_r)
            owners += who[j + len(old) - len(keep_r):j + len(old)]
            i = j + len(old)
        out.append(t[i:])
        owners += who[i:]
        t, who = ''.join(out), owners
    return t, who


_BRACES = re.compile(r'\{[^{}]*\}')
OPEN, MID, CLOSE, KEEP = '\ue030', '\ue031', '\ue032', '\ue010'


def mark(text, who):
    """The text with markers around braced errata and corrected words; the popups' texts."""
    brace = [0] * len(text)
    for m in _BRACES.finditer(text):
        for k in range(m.start(), m.end()):
            brace[k] = 1
    out, infos, k = [], [], 0
    while k < len(text):
        key = (brace[k], tuple(id(x) for x in who[k]))
        j = k
        while j < len(text) and (brace[j], tuple(id(x) for x in who[j])) == key and (text[j] != '\n' or j == k):
            j += 1
        chunk, owners = text[k:j], who[k]
        if chunk == '\n' or (not brace[k] and not owners):
            out.append(chunk)
        else:
            classes, lines = [], []
            if brace[k]:
                classes.append('erratum')
                lines.append('GRETIL erratum: this word is printed between braces { } in GRETIL. '
                             'It is kept as printed; its content is not altered.')
            for c in owners:
                classes.append('correction')
                when = f"approved on {c['date']}" if c['date'] else 'approved in the corrections layer'
                lines.append(f"Correction {when}. Source: {c['source']}. "
                             f"GRETIL had: «{c['gretil'].strip()}». The book prints: «{c['book'].strip()}».")
            infos.append((' '.join(dict.fromkeys(classes)), ' | '.join(dict.fromkeys(lines))))
            out.append(f'{OPEN}{len(infos) - 1}{MID}{chunk}{CLOSE}')
        k = j
    return ''.join(out), infos


def spans(block, infos):
    def open_(m):
        cls, info = infos[int(m.group(1))]
        return f'<span class="{cls}" data-info="{html.escape(info, quote=True)}">'
    return re.sub(OPEN + r'(\d+)' + MID, open_, block).replace(CLOSE, '</span>')


_SUPERSCRIPTS = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789')
_SUPERSCRIPT = re.compile(r'\s*([⁰¹²³⁴⁵⁶⁷⁸⁹]+)')
_NOTE_DASH = '-' * 74


def red(n):
    return f'<span class="red"><sup>{n}</sup></span>'


def page_html(n, head, lines, notes):
    """A page in the format of GRETIL's files."""
    t = html.escape('\n'.join(lines), quote=False).replace('||||', '|| ||')
    t = _SUPERSCRIPT.sub(lambda m: red(m.group(1).translate(_SUPERSCRIPTS)), t)
    s = [f'<!-- page-status: corrected --><b>[page {n:03d}]</b><BR>\n']
    if head:
        s.append(f'<i>{html.escape(head, quote=False)}</i><BR>\n')
    if lines:
        s.append(''.join(r + '<BR>\n' for r in t.split('\n')))
    if notes:
        s.append(f'<span class="red">{_NOTE_DASH}<BR>\n')
        s += [html.escape(r.translate(_SUPERSCRIPTS), quote=False) + '<BR>\n' for r in notes.split('\n')]
        s.append('</span><BR>\n')
    return ''.join(s)


STYLE = """<style>
body{font-family:Georgia,serif;max-width:60em;margin:1em auto;padding:0 1em;color:#222}
.erratum{border-bottom:2px solid #c00;cursor:help}
.correction{text-decoration:underline #05c 2px;cursor:help}
.erratum.correction{border-bottom:2px solid #c00}
#tip{position:fixed;display:none;max-width:26em;background:#fffbe6;border:1px solid #888;
 padding:.5em .7em;font:13px/1.4 sans-serif;box-shadow:0 2px 6px #0004;z-index:9;white-space:normal}
.legend{font:13px/1.4 sans-serif;border:1px solid #ccc;padding:.5em .8em;margin-bottom:1em}
</style>"""
SCRIPT = """<script>
(function(){var tip=document.createElement('div');tip.id='tip';document.body.appendChild(tip);
function show(el,x,y){tip.textContent=el.getAttribute('data-info').split(' | ').join('\\n');
tip.style.whiteSpace='pre-line';tip.style.display='block';
tip.style.left=Math.min(x+12,innerWidth-tip.offsetWidth-8)+'px';tip.style.top=(y+16)+'px';}
document.addEventListener('mousemove',function(e){var el=e.target.closest&&e.target.closest('[data-info]');
if(el)show(el,e.clientX,e.clientY);else tip.style.display='none';});
document.addEventListener('click',function(e){var el=e.target.closest&&e.target.closest('[data-info]');
if(el)show(el,e.clientX,e.clientY);});})();
</script>"""
WARNING = ('<div class="legend" style="border:2px solid #c00;background:#fff4f4"><b>IMPORTANT: the critical '
           'apparatus has NOT been proofread.</b> The corrections marked in this file apply to the '
           'main text only. The footnotes and variant readings (the critical apparatus) are exactly '
           'as GRETIL prints them and have not been submitted to proofreading against the printed '
           'edition; they may contain errors and should not be relied on without checking the book.</div>\n')
CREDIT = ('<div class="legend"><b>About this copy.</b> The licence and the notice above are GRETIL\'s '
          'own and apply unchanged (CC BY-SA 4.0, &copy; Pali Text Society and Dhammakaya Foundation, 2015). '
          'Manual proofreading corrections against the scans of the printed edition are marked below '
          '(Jorge Contreras, github.com/jorgecaa, foureditions project); each was approved by a person. '
          'Corrections derived from the Cone dictionary, Jackson\'s revised Sa\u1e43yutta IV apparatus or '
          'word indices are identified by their source label. '
          'The text of GRETIL itself has not been rewritten: every correction is recorded, with its '
          'source and date, in corrections.json of the repository that built this file.</div>\n')
LEGEND = ('<div class="legend"><span class="erratum">red underline</span>: an erratum that GRETIL '
          'prints between braces { }; kept as printed. &nbsp; <span class="correction">blue underline</span>: '
          'a correction approved in the foureditions project. Hover over (or tap) a marked word for '
          'its source, the date it was approved, and what GRETIL had.</div>')
NOTE = ('Pali Text Society edition (Ee), digital input by the Dhammakaya Foundation (1989-1996), GRETIL '
        'version. Licence: CC BY-SA 4.0, (c) Pali Text Society and Dhammakaya Foundation, 2015. '
        'This file carries the corrections approved in the foureditions project ({count} pages '
        'changed in this file, generated {date}). The critical apparatus (footnotes and variant '
        'readings) has NOT been proofread. Text between braces is an erratum printed by GRETIL and '
        'is kept as is. The original GRETIL file is not modified.')


def document(header, note, blocks):
    """GRETIL's own opening (title, introduction, licence notice, terms of use) is kept as it is."""
    start = header.lower().find('<!doctype')
    head = re.sub(r'(<title>)\s*(.*?)\s*(</title>)', r'\1\2 (with approved corrections marked)\3',
                  header[start:] if start > 0 else header, count=1, flags=re.S)
    head = head.replace('</head>', STYLE + '</head>', 1)
    return (head + f'<!-- {note} -->\n{WARNING}{CREDIT}{LEGEND}<hr>\n' + ''.join(blocks)
            + f'<hr>\n{SCRIPT}</body></html>\n')


def build_file(volume, rel):
    with open(os.path.join(BASE, rel + '.htm'), encoding='utf-8', newline=None) as fh:
        source = _BR.sub('<BR>', fh.read())
    if unicodedata.normalize('NFC', source) != source:
        sys.exit(f'{rel}: not in Unicode NFC')
    header = _PAGE.split(source)[0]
    blocks, changed = [], 0
    for n, (head, text, notes) in sorted(parts(source).items()):
        replaced = DATA['replaced_pages'].get(f'{volume}|{n}')
        if replaced:
            head, text, notes = replaced['head'], replaced['text'], replaced['notes']
            who = [()] * len(text)
        else:
            head, _ = apply(volume, n, 'head', head)
            notes, _ = apply(volume, n, 'notes', notes)
            text, who = apply(volume, n, 'text', text)
            if volume.startswith('SN '):          # the Saṃyutta writes its abbreviation sign as `°`
                text = text.replace('º', '°')
        changed += any(who)
        marked, infos = mark(text, who)
        block = page_html(n, head, marked.replace('ṁ', KEEP).split('\n'), notes).replace(KEEP, 'ṁ')
        block = spans(block, infos)
        # the page reads back exactly as written
        back = parts(block, abbreviate=False)[n]
        if back[1].rstrip('\n') != text.replace('||', '║').rstrip('\n') or back[0] != head \
                or back[2].strip() != notes.strip():
            sys.exit(f'{volume} p. {n}: does not read back identical')
        blocks.append(block)
    os.makedirs(OUT_DIR, exist_ok=True)
    note = NOTE.format(count=changed, date=datetime.date.today().isoformat())
    with open(os.path.join(OUT_DIR, os.path.basename(rel) + '.htm'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(document(header, note, blocks))
    print(f'{os.path.basename(rel)}.htm: {len(blocks)} pages, {changed} with corrections')


def main():
    if '--verify' not in sys.argv:
        download()
    verify()
    if '--verify' in sys.argv:
        print('the downloaded files are the ones the corrections were made on')
        return
    for volume, rels in FILES.items():
        for rel in rels:
            build_file(volume, rel)


if __name__ == '__main__':
    main()
