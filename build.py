#!/usr/bin/env python3
"""Rebuild the corrected GRETIL files.

Licence of this repository (code, data and built files): CC BY-SA 4.0, the licence of the GRETIL
files it derives from (see README.md).

    python3 build.py            # 1. download  2. read corrections.json  3. write corrected/*.htm
    python3 build.py --verify   # only check that the downloaded files are the ones corrections.json expects

Needs Python 3.9+ and git. No other dependency. See README.md.
"""
import difflib
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
    """The pinned commit of the mirror, only the Pāli folders (about 150 MB on disk)."""
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
    if not os.path.isdir(BASE):
        sys.exit('GRETIL has not been downloaded yet: run `python3 build.py` first')
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


CALL_OPEN, CALL_CLOSE = '\ue020', '\ue021'


def body(chunk, abbreviate=True, keep_calls=False):
    """The body of a GRETIL page: note calls as digits, GRETIL's markers removed, the
    abbreviation sign `º` and the elision apostrophe `’` rebuilt from GRETIL's hyphen and `';`.
    With `keep_calls`, every note call stays between two marks, to know afterwards which digits are calls."""
    c = _CALL.sub(CALL_OPEN + r'\1' + CALL_CLOSE if keep_calls else r'\1', chunk)
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


def call_flags(chunk, text):
    """For every character of `text` (the body of the page), whether it belongs to a note call.
    The page is read again with its calls marked; if that reading does not give the same text,
    nothing is flagged (the calls of that page stay as plain digits)."""
    flags, plain_text, inside = [], [], False
    for ch in body(chunk, keep_calls=True):
        if ch == CALL_OPEN:
            inside = True
        elif ch == CALL_CLOSE:
            inside = False
        else:
            plain_text.append(ch)
            flags.append(inside)
    return flags if ''.join(plain_text) == text else None


_GLUED = re.compile(r'(?<=[^\s\d])\d+')


def glued_calls(text):
    """Where GRETIL does not tell (a page read from the scan, or one that cannot be read twice the
    same way): the digits glued to the end of a word are its note calls; a paragraph number stands alone."""
    flags = [False] * len(text)
    for m in _GLUED.finditer(text):
        flags[m.start():m.end()] = [True] * (m.end() - m.start())
    return flags


def parts(source, abbreviate=True, calls=None):
    """`{page: (running head, body, footnotes)}` of a whole GRETIL file. `calls`, a dict, receives
    for each page the flags of `call_flags`."""
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
        if calls is not None:
            calls[int(z[i])] = call_flags(c, out[int(z[i])][1])
    return out


# 3. apply the corrections, write the pages -------------------------------------------------

CORRECTIONS = {}
for c in DATA['corrections']:
    CORRECTIONS.setdefault((c['volume'], c['page']), []).append(c)


def _tokens(t):
    return re.split(r'(\s+)', t)


def _trim(old, new):
    """The words that change, and the unchanged context around them (split at whitespace)."""
    a, b = _tokens(old), _tokens(new)
    i = 0
    while i < min(len(a), len(b)) and a[i] == b[i]:
        i += 1
    j = 0
    while j < min(len(a), len(b)) - i and a[-1 - j] == b[-1 - j]:
        j += 1
    if not ''.join(a[i:len(a) - j]).strip() and not ''.join(b[i:len(b) - j]).strip():
        # only the spacing changes (two lines joined): the words on either side are the correction
        i, j = max(i - 1, 0), max(j - 1, 0)
    return ''.join(a[:i]), ''.join(a[i:len(a) - j]), ''.join(b[i:len(b) - j]), ''.join(a[len(a) - j:])


def apply(volume, n, part, text, flags=None):
    """The text with its corrections; for every character, the corrections that wrote it and
    whether it belongs to a note call."""
    t, who = text, [()] * len(text)
    call = list(flags) if flags else [False] * len(text)
    for c in CORRECTIONS.get((volume, n), []):
        if c.get('part', 'text') != part:
            continue
        old, new = c['gretil'], c['book']
        if c.get('kind') == 'emendation':
            # an authority's correction of the edition: the text stays as printed, the words are only marked
            at = [j for j in range(len(t)) if t.startswith(old, j)]
            if len(at) != c['times']:
                # the emendation was written on the text with the earlier emendations of the page applied:
                # where one of them stands, its words are no longer there to be found
                at = [j for j in at if not any(x.get('kind') == 'emendation' for w in who[j:j + len(old)] for x in w)]
            if len(at) != c['times']:
                sys.exit(f'{volume} p. {n}: {old!r} is there {len(at)} times, the correction says {c["times"]}')
            keep_l, mid_old, _, _ = _trim(old, new)
            a, b = len(keep_l), len(keep_l) + len(mid_old)
            if not mid_old.strip():         # an addition: the words it would follow or precede are marked
                a, b = len(old) - len(old.lstrip()), len(old.rstrip())
            who = list(who)
            for j in at:
                for x in range(j + a, j + b):
                    who[x] = who[x] + (c,)
            continue
        if t.count(old) != c['times']:
            sys.exit(f'{volume} p. {n}: {old!r} is there {t.count(old)} times, the correction says {c["times"]}')
        # only the words that change are marked: what the correction repeats around them (a
        # line-break hyphen, a neighbouring word) is context, not part of the correction
        keep_l, mid_old, mid_new, keep_r = _trim(old, new)
        out, owners, calls, i = [], [], [], 0
        gone = not mid_new.strip() and mid_old.strip()      # words deleted: nothing of the correction is left
        where, length = [], 0                               # where, in the new text, the deleted words stood
        while True:
            j = t.find(old, i)
            if j < 0:
                break
            a, b = j + len(keep_l), j + len(keep_l) + len(mid_old)
            where.append(length + (j - i) + len(keep_l))
            length += (j - i) + len(keep_l) + len(mid_new) + len(keep_r)
            out.append(t[i:j] + keep_l + mid_new + keep_r)
            owners += who[i:a]
            owners += [tuple(x for w in who[a:b] for x in w) + (c,)] * len(mid_new)
            owners += who[b:j + len(old)]
            # a note call that the correction keeps is still a call
            kept = [False] * len(mid_new)
            for m in difflib.SequenceMatcher(None, mid_old, mid_new, autojunk=False).get_matching_blocks():
                kept[m.b:m.b + m.size] = call[a + m.a:a + m.a + m.size]
            calls += call[i:a] + kept + call[b:j + len(old)]
            i = j + len(old)
        out.append(t[i:])
        owners += who[i:]
        calls += call[i:]
        t, who, call = ''.join(out), owners, calls
        if gone:
            # a deletion is shown on the word before it (or, at the start, the word after it)
            for w in where:
                x = w
                while x > 0 and t[x - 1].isspace():
                    x -= 1
                y = x
                while y > 0 and not t[y - 1].isspace():
                    y -= 1
                if x == y:
                    y = w
                    while y < len(t) and t[y].isspace():
                        y += 1
                    x = y
                    while x < len(t) and not t[x].isspace():
                        x += 1
                for z in range(min(x, y), max(x, y)):
                    who[z] = who[z] + (c,)
    return t, who, call


_BRACES = re.compile(r'\{[^{}]*\}')
OPEN, MID, CLOSE, KEEP = '\ue030', '\ue031', '\ue032', '\ue010'


def _with_calls(text, call, k, j):
    """`text[k:j]` with its note calls between marks."""
    out = []
    for x in range(k, j):
        on, before, after = call[x], x > k and call[x - 1], x + 1 < j and call[x + 1]
        out.append((CALL_OPEN if on and not before else '') + text[x] + (CALL_CLOSE if on and not after else ''))
    return ''.join(out)


BRACES_NOTE = ('GRETIL encloses this in braces { }. | Reproduced as in GRETIL: the proofreading left '
               'the content between braces unchanged, except for notation.')


def describe(c):
    """The popup's text for one correction; ` | ` separates its lines."""
    _, old, new, _ = _trim(c['gretil'], c['book'])        # only the words that change
    old, new = ' '.join(old.split()), ' '.join(new.split())
    full_old, full_new = ' '.join(c['gretil'].split()), ' '.join(c['book'].split())
    date = f"Approved on {c['date']}." if c['date'] else 'Approval date not recorded.'
    kind = c.get('kind', 'transcription')
    if kind == 'emendation':
        # listing an emendation does not endorse it: its date is when it was recorded
        date = f"Recorded on {c['date']}." if c['date'] else 'Date not recorded.'
        if not old or not new:                            # an addition or an omission: show the context
            old, new = full_old, full_new
        lines = ['Suggested emendation (not applied to the text)', f'Text, as in GRETIL: «{old}»',
                 f'Suggested: «{new}»', f"Authority: {c['source']}. {date}"]
    elif kind == 'notation':
        lines = ['Notation only (same reading)', f'GRETIL: «{old}» → «{new}» (same letters; only the signs differ)',
                 date]
    elif c['gretil'] == c['book']:
        lines = ['Printed reading confirmed', f'The printed edition reads «{new}» (sic), as GRETIL has; kept.',
                 f"Evidence: {c['source']}. {date}"]
    elif old == new:
        lines = ['Line division corrected', f'Same reading: «{new}»', f"Evidence: {c['source']}. {date}"]
    elif not old:
        lines = ['Transcription corrected', f'GRETIL omits «{new}»; the printed edition has it.',
                 f"Evidence: {c['source']}. {date}"]
    elif not new:
        lines = ['Transcription corrected', f'GRETIL has «{old}» next to the marked word; the printed edition does not have it.',
                 f"Evidence: {c['source']}. {date}"]
    else:
        lines = ['Transcription corrected', f'GRETIL: «{old}» → printed edition: «{new}»',
                 f"Evidence: {c['source']}. {date}"]
    return ' | '.join(lines)


def mark(text, who, call, infos=None, braces=True, tag='span'):
    """The text with markers around braced errata, corrected words and note calls; the popups' texts."""
    brace = [0] * len(text)
    for m in _BRACES.finditer(text) if braces else ():
        for k in range(m.start(), m.end()):
            brace[k] = 1
    out, k = [], 0
    infos = [] if infos is None else infos
    while k < len(text):
        key = (brace[k], tuple(id(x) for x in who[k]))
        j = k
        while j < len(text) and (brace[j], tuple(id(x) for x in who[j])) == key and (text[j] != '\n' or j == k):
            j += 1
        chunk, owners = _with_calls(text, call, k, j), who[k]
        if not chunk.strip() or (not brace[k] and not owners):     # spacing alone is not underlined
            out.append(chunk)
        else:
            classes, items = [], []
            if brace[k]:
                classes.append('erratum')
                items.append(BRACES_NOTE)
            for c in owners:
                classes.append('suggestion' if c.get('kind') == 'emendation' else 'correction')
                items.append(describe(c))
            infos.append((' '.join(dict.fromkeys(classes)), ' |  | '.join(dict.fromkeys(items)), tag))
            out.append(f'{OPEN}{len(infos) - 1}{MID}{chunk}{CLOSE}')
        k = j
    return ''.join(out), infos


def spans(block, infos):
    def open_(m):
        cls, info, tag = infos[int(m.group(1))]
        return f'<{tag} class="{cls}" data-info="{html.escape(info, quote=True)}">'
    block = re.sub(OPEN + r'(\d+)' + MID, open_, block)
    # each mark is closed by the tag it was opened with
    out, stack = [], []
    for piece in re.split('(<(?:span|u) class="[^"]*" data-info="[^"]*">|' + CLOSE + ')', block):
        if piece == CLOSE:
            out.append(f'</{stack.pop()}>')
        else:
            if piece.startswith('<u class='):
                stack.append('u')
            elif piece.startswith('<span class=') and 'data-info=' in piece:
                stack.append('span')
            out.append(piece)
    return ''.join(out)


_SUPERSCRIPTS = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789')
_SUPERSCRIPT = re.compile(r'\s*([⁰¹²³⁴⁵⁶⁷⁸⁹]+)')
_NOTE_DASH = '-' * 74


def red(n):
    return f'<span class="red"><sup>{n}</sup></span>'


def page_html(n, head, lines, notes):
    """A page in the format of GRETIL's files."""
    t = html.escape('\n'.join(lines), quote=False).replace('||||', '|| ||')
    t = _SUPERSCRIPT.sub(lambda m: red(m.group(1).translate(_SUPERSCRIPTS)), t)
    t = re.sub(CALL_OPEN + '(.*?)' + CALL_CLOSE, lambda m: red(m.group(1)), t)
    s = [f'<!-- page-status: corrected --><b>[page {n:03d}]</b><BR>\n']
    if head:
        s.append(f'<i>{html.escape(head, quote=False)}</i><BR>\n')
    if lines:
        # line numbers of the body only (not the running head, not the apparatus): 1, 5, 10, 15…
        # They are drawn by the style sheet from `data-n`, so they are not part of the text.
        k = 0
        for r in t.split('\n'):
            if not r.strip():
                s.append(r + '<BR>\n')
                continue
            k += 1
            n_attr = f' data-n="{k}"' if k == 1 or k % 5 == 0 else ''
            s.append(f'<span class="ln"{n_attr}></span>' + r + '<BR>\n')
    if notes:
        s.append(f'<span class="red">{_NOTE_DASH}<BR>\n')
        s += [html.escape(r.translate(_SUPERSCRIPTS), quote=False) + '<BR>\n' for r in notes.split('\n')]
        s.append('</span><BR>\n')
    return ''.join(s)


STYLE = """<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans:ital,wght@0,400;0,700;1,400&display=swap">
<style>
body,td{font-family:'Noto Sans',sans-serif}
body{max-width:60em;margin:1em auto;padding:0 1em;color:#222;line-height:1.4;word-spacing:5px}
.erratum{border-bottom:2px solid #c00;cursor:help}
.correction{text-decoration:underline #3cb371 2px;text-underline-offset:.32em;text-decoration-skip-ink:none;cursor:help}
.erratum.correction{border-bottom:2px solid #c00}
.suggestion{border-bottom:2px dotted #d07a00;cursor:help}
u.suggestion,u.erratum{text-decoration:none}
#tip{position:fixed;display:none;max-width:26em;background:#fffbe6;border:1px solid #888;
 padding:.5em .7em;font:13px/1.4 'Noto Sans',sans-serif;box-shadow:0 2px 6px #0004;z-index:9;white-space:pre-line;word-spacing:normal}
.red{color:#00c}
.ln{display:inline-block;width:2.2em;margin-right:.9em;text-align:right;color:#000;font:11px/1 'Noto Sans',sans-serif;
 user-select:none;vertical-align:baseline}
.ln::before{content:attr(data-n)}
.legend{font:13px/1.4 'Noto Sans',sans-serif;border:1px solid #ccc;padding:.5em .8em;margin-bottom:1em}
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
          'Where GRETIL departs from the printed edition, the text below gives the printed reading, '
          'checked against the scans of the edition; proofreading and approval by Jorge Contreras '
          '(github.com/jorgecaa), foureditions project. Each correction was approved by a person; 24 were '
          'read on the scan by machine and checked by hand, as their popups say.{replaced} The proofreader is not a philologist. The corrections are mechanical: each one restores what the printed PTS edition prints, read on its scan, or records an emendation proposed by the authority cited. No reading was chosen on text-critical grounds, and no emendation is the proofreader\'s own; listing an emendation does not endorse it. Emendations of the edition itself (M. Cone\'s '
          'Dictionary of P\u0101li, P. Jackson\'s revision of Sa\u1e43yutta IV, W. Pruitt\'s correction lists) '
          'are not applied to the text: they are given as suggestions on the words concerned. '
          'The text of GRETIL itself has not been rewritten: every correction is recorded, with its '
          'source and, when recorded, its date, in corrections.json of the repository that built this file.</div>\n')
#: said only in a file with pages read from the scan in place of GRETIL's (`replaced_pages`)
REPLACED = {'SN II': (' Pages 109-116, missing or cut short in GRETIL, were read from the scan by machine '
                      '(OCR for 109-112, AI for 113-116) and reviewed by hand; they carry no marks.')}
LEGEND = ('<div class="legend"><span class="erratum">red underline</span>: GRETIL encloses the words in '
          'braces { }; reproduced as in GRETIL, unchanged except for notation. &nbsp; '
          '<span class="correction">green underline</span>: '
          'GRETIL departs from the printed edition; the printed reading is given. &nbsp; '
          '<span class="suggestion">orange dotted underline</span>: an emendation of the edition, suggested '
          'but not applied. Hover over (or tap) a marked word for the readings, the evidence or authority, '
          'and the approval date when recorded.</div>')
NOTE = ('Pali Text Society edition (Ee), digital input by the Dhammakaya Foundation (1989-1996), GRETIL '
        'version. Licence: CC BY-SA 4.0, (c) Pali Text Society and Dhammakaya Foundation, 2015. '
        'This file carries the corrections approved in the foureditions project ({count} pages '
        'changed in this file; built from commit {commit} of the GRETIL mirror). The critical apparatus (footnotes and variant '
        'readings) has NOT been proofread. Text between braces is reproduced as GRETIL has it, '
        'unchanged except for notation. Emendations of the edition are suggested, not applied. '
        'The original GRETIL file is not modified.')


#: volumes whose footnotes were proofread too: the warning about the apparatus does not apply
APPARATUS_PROOFREAD = ('Sn',)


def document(header, note, blocks, warning, credit):
    """GRETIL's own opening (title, introduction, licence notice, terms of use) is kept as it is;
    the warning about the apparatus, when it applies, stands above it, at the top of the page."""
    start = header.lower().find('<!doctype')
    head = re.sub(r'(<title>)\s*(.*?)\s*(</title>)', r'\1\2 (with approved corrections marked)\3',
                  header[start:] if start > 0 else header, count=1, flags=re.S)
    head = head.replace('</head>', STYLE + '</head>', 1)
    head = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + '\n' + warning, head, count=1)
    return (head + f'<!-- {note} -->\n{credit}{LEGEND}<hr>\n' + ''.join(blocks)
            + f'<hr>\n{SCRIPT}</body></html>\n')


def build_file(volume, rel):
    with open(os.path.join(BASE, rel + '.htm'), encoding='utf-8', newline=None) as fh:
        source = _BR.sub('<BR>', fh.read())
    if unicodedata.normalize('NFC', source) != source:
        sys.exit(f'{rel}: not in Unicode NFC')
    header = _PAGE.split(source)[0]
    blocks, changed, calls = [], 0, {}
    for n, (head, text, notes) in sorted(parts(source, calls=calls).items()):
        replaced = DATA['replaced_pages'].get(f'{volume}|{n}')
        if replaced:
            head, text, notes = replaced['head'], replaced['text'], replaced['notes']
            who, call = [()] * len(text), glued_calls(text)
            head_who, notes_who = [()] * len(head), [()] * len(notes)
        else:
            head, head_who, _ = apply(volume, n, 'head', head)
            notes, notes_who, _ = apply(volume, n, 'notes', notes)
            text, who, call = apply(volume, n, 'text', text, calls[n] or glued_calls(text))
            if volume.startswith('SN '):          # the Saṃyutta writes its abbreviation sign as `°`
                text = text.replace('º', '°')
        changed += any(who) or any(head_who) or any(notes_who)
        marked, infos = mark(text, who, call)
        # the running head and the apparatus: corrected words are marked, braces are not
        # (`<u>`, not `<span>`: GRETIL's apparatus is itself a span, which a nested span would cut short)
        head_marked = mark(head, head_who, [False] * len(head), infos, braces=False, tag='u')[0]
        notes_marked = mark(notes, notes_who, [False] * len(notes), infos, braces=False, tag='u')[0]
        block = page_html(n, head_marked, marked.replace('ṁ', KEEP).split('\n'), notes_marked).replace(KEEP, 'ṁ')
        block = spans(block, infos)
        # the page reads back exactly as written
        back = parts(block, abbreviate=False)[n]
        if back[1].rstrip('\n') != text.replace('||', '║').rstrip('\n') or back[0] != head \
                or back[2].strip() != notes.strip():
            sys.exit(f'{volume} p. {n}: does not read back identical')
        blocks.append(block)
    os.makedirs(OUT_DIR, exist_ok=True)
    proofread = volume in APPARATUS_PROOFREAD
    note = NOTE.format(count=changed, commit=DATA['commit'][:12])
    if proofread:
        note = note.replace(' The critical apparatus (footnotes and variant readings) has NOT been proofread.', '')
    with open(os.path.join(OUT_DIR, os.path.basename(rel) + '.htm'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(document(header, note, blocks, '' if proofread else WARNING,
                          CREDIT.replace('{replaced}', REPLACED.get(volume, ''))))
    print(f'{os.path.basename(rel)}.htm: {len(blocks)} pages, {changed} with corrections')
    return len(blocks)


INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PTS Pali texts from GRETIL, proofread</title>
{style}
</head>
<body>
<h1>PTS Pali texts from GRETIL, proofread</h1>
<p>The Pali Text Society editions as GRETIL gives them (digital input by the Dhammakaya Foundation),
with proofreading corrections against the scans of the printed editions marked in the text. Built
reproducibly from a pinned commit of the GRETIL mirror; source, method and licence:
<a href="https://github.com/jorgecaa/pts-gretil-ng">github.com/jorgecaa/pts-gretil-ng</a>.</p>
{legend}
<p><b>The critical apparatus (footnotes) has NOT been proofread</b>, except in the Sutta Nipāta.
Licence: CC BY-SA 4.0, &copy; Pali Text Society and Dhammakaya Foundation, 2015.</p>
<p>Every volume listed with a file was reviewed in the foureditions review service. The counts give the
corrections approved so far. A volume with 0 corrections applied has no approved correction yet; this
does not mean it was proofread in full and found free of errors, since the proofreading is not finished
for every book. Ja I carries only suggested emendations, which do not change the text.</p>
<p>Struck through, at the end: the books the review service leaves out, which are not built. A review needs
a scan of the same printed edition that GRETIL transcribes; six of these books have none usable, and the
Yamaka is excluded:</p>
<ul>
<li><b>Vimānavatthu and Petavatthu, Buddhavaṃsa and Cariyāpiṭaka</b>: GRETIL gives the later PTS editions by
N. A. Jayawickrama (1977 and 1974); the scans at hand are of the earlier editions (Gooneratne 1886,
Minayeff 1888, Morris 1882), a different text.</li>
<li><b>Apadāna</b>: the scan at hand was withdrawn, because its images lose the diacritics.</li>
<li><b>Paṭṭhāna</b>: no scan of the PTS edition is at hand.</li>
<li><b>Yamaka</b>: its PTS edition is excluded from the review because of its many abbreviations.</li>
</ul>
<table>
<tr><th>Volume</th><th>File</th><th>Pages</th><th>Corrections applied</th><th>Emendations suggested</th></tr>
{rows}
</table>
</body>
</html>
"""


#: the books the foureditions review service leaves out: not reviewed, so not built (README, «Volumes»)
NO_SCAN = 'not reviewed: the review service has no compatible scan of the printed PTS edition'
LEFT_OUT = (('Vimānavatthu', NO_SCAN), ('Petavatthu', NO_SCAN), ('Apadāna', NO_SCAN),
            ('Buddhavaṃsa', NO_SCAN), ('Cariyāpiṭaka', NO_SCAN),
            ('Yamaka', 'not reviewed: the review service excludes its PTS edition (too many abbreviations)'),
            ('Paṭṭhāna', NO_SCAN))


def write_index(pages):
    """`index.html`: the page GitHub Pages opens first, with a link to every built file."""
    # applied corrections and suggested emendations apart: an emendation does not change the text
    counts, emended = {}, {}
    for c in DATA['corrections']:
        tally = emended if c.get('kind') == 'emendation' else counts
        tally[c['volume']] = tally.get(c['volume'], 0) + 1
    rows = []
    for volume, rels in FILES.items():
        for k, rel in enumerate(rels):
            name = os.path.basename(rel) + '.htm'
            rows.append(f'<tr><td>{html.escape(volume) if k == 0 else ""}</td>'
                        f'<td><a href="corrected/{name}">{name}</a></td><td>{pages[rel]}</td>'
                        f'<td>{counts.get(volume, 0) if k == 0 else ""}</td>'
                        f'<td>{emended.get(volume, 0) if k == 0 else ""}</td></tr>')
    for book, reason in LEFT_OUT:                         # struck through: not reviewed, not built
        rows.append(f'<tr><td><s>{html.escape(book)}</s></td><td colspan="4">{html.escape(reason)}</td></tr>')
    style = STYLE.replace('</style>', 'table{border-collapse:collapse}td,th{padding:.2em .8em;text-align:left}'
                          'td:nth-child(n+3){text-align:right}tr:nth-child(even){background:#f4f4f4}</style>')
    with open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(INDEX.format(style=style, legend=LEGEND, rows='\n'.join(rows)))


def main():
    if '--verify' not in sys.argv:
        download()
    verify()
    if '--verify' in sys.argv:
        print('the downloaded files are the ones the corrections were made on')
        return
    pages = {}
    for volume, rels in FILES.items():
        for rel in rels:
            pages[rel] = build_file(volume, rel)
    write_index(pages)


if __name__ == '__main__':
    main()
