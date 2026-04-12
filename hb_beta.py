# FIXME:Remove after beta
import difflib


def diff_filter(new: str, old: str):
    ret = ''

    old_words = old.split()
    new_words = new.split()

    matcher = difflib.SequenceMatcher(None, old_words, new_words)
    ret = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            ret.extend(old_words[i1:i2])
        elif tag == 'delete':
            deleted = ' '.join(old_words[i1:i2])
            ret.append(f'<span class="diff removed">{deleted}</span>')
        elif tag == 'insert':
            inserted = ' '.join(new_words[j1:j2])
            ret.append(f'<span class="diff added">{inserted}</span>')
        elif tag == 'replace':
            deleted = ' '.join(old_words[i1:i2])
            inserted = ' '.join(new_words[j1:j2])
            # Shortcut to deal with added or removed puncutuation.
            if deleted + '.' == inserted:
                ret.append(deleted + '<span class="diff added">.</span>')
            elif deleted == inserted + '.':
                ret.append(inserted + '<span class="diff removed">.</span>')
            else:
                ret.append(f'<span class="diff removed">{deleted}</span>' +
                           f'<span class="diff added">{inserted}</span>')
    return ' '.join(ret)
