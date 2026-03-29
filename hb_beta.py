# FIXME:Remove after beta
import difflib


def diff_filter(new: str, old: str):
    ret = ''

    old_words = old.split()
    new_words = new.split()

    matcher = difflib.SequenceMatcher(None, old_words, new_words)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            ret += ' '.join(old_words[i1:i2])
        elif tag == 'delete':
            ret += f'<span class="diff removed">{" ".join(old_words[i1:i2])}</span>'
        elif tag == 'insert':
            ret += f'<span class="diff added">{" ".join(new_words[j1:j2])}</span>'
        elif tag == 'replace':
            ret += f'<span class="diff removed">{" ".join(old_words[i1:i2])}</span>'
            ret += f'<span class="diff added">{" ".join(new_words[j1:j2])}</span>'
    return ret
