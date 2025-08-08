from pathlib import Path


def resolve_conflicts_keep_head(text: str) -> str:
    output_parts = []
    i = 0
    while True:
        start = text.find('<<<<<<< HEAD', i)
        if start == -1:
            output_parts.append(text[i:])
            break
        output_parts.append(text[i:start])
        mid = text.find('=======', start)
        end = text.find('>>>>>>>', mid)
        if mid == -1 or end == -1:
            # If markers are broken, append rest and stop to avoid damaging file
            output_parts.append(text[start:])
            break
        head_part = text[start + len('<<<<<<< HEAD'): mid]
        output_parts.append(head_part)
        # move index to after the end marker line
        newline_after_end = text.find('\n', end)
        i = len(text) if newline_after_end == -1 else newline_after_end + 1
    return ''.join(output_parts)


def main():
    target = Path('main.py')
    if not target.exists():
        print('main.py not found')
        return
    original = target.read_text(encoding='utf-8')
    resolved = resolve_conflicts_keep_head(original)
    if resolved != original:
        target.write_text(resolved, encoding='utf-8')
        print('Conflicts resolved in main.py')
    else:
        print('No conflicts found in main.py')


if __name__ == '__main__':
    main()


