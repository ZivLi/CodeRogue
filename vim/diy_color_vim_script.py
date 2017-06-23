def change_context(file_path, change_file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    lines = map(format_line, lines)
    with open(change_file_path, 'w') as f:
        f.writelines(lines)


def format_line(line):
    if not line.startswith('hi'):
        return line
    line = line.replace('gui', 'cterm')
    line = '{}ctermfg={}'.format(line.split('ctermfg=')[0], line.split('ctermfg=')[1])+'\n'
    return line


if __name__ == '__main__':
    change_context("/Users/zivli/.vim/colors/cor_back_up.vim",
                   "/Users/zivli/.vim/colors/corporation.vim")
