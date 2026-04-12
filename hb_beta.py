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
            deleted = ' '.join(old_words[i1:i2])
            inserted = ' '.join(new_words[j1:j2])
            # Shortcut to deal with added or removed puncutuation.
            if deleted + '.' == inserted:
                ret += deleted + '<span class="diff added">.</span>'
            elif deleted == inserted + '.':
                ret += inserted + '<span class="diff removed">.</span>'
            else:
                ret += f'<span class="diff removed">{deleted}</span>'
                ret += f'<span class="diff added">{inserted}</span>'
    return ret
