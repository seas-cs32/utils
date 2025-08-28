### utils/strip_notes.py
'''Removes notebook cells labeled as `notes` so that the notebook
   can be distributed to the students. If you call this script with
   the parameter `yourfile.ipynb`, it will write the stripped file
   to `yourfile-nonotes.ipynb`.'''

import sys
import nbformat

def main():
    if len(sys.argv) == 2:
        in_fname = sys.argv[1]
        assert in_fname[-6:] == '.ipynb', 'Bad input file'
        out_fname = in_fname[:-6] + '-nonotes.ipynb'
    else:
        sys.exit('Usage: python3 strip_notes.py yourfile.ipynb')

    # Read the input notebook
    with open(in_fname) as fin:
        nb = nbformat.read(fin, as_version=4)

    print(f'Processing {in_fname}, which contains {len(nb.cells)} cells')

    for i in range(len(nb.cells) - 1, -1, -1):
        cell = nb.cells[i]
        if cell.metadata:
            if 'slideshow' in cell.metadata:
                if 'slide_type' in cell.metadata['slideshow']:
                    stype = cell.metadata['slideshow']['slide_type']
                    if stype == 'notes':
                        print(f'Deleting cell {i}')
                        del nb.cells[i]
        else:
            print(f'Cell {i} has no metadata')

    # Write out the modified notebook
    with open(out_fname, 'w', encoding='utf-8') as fout:
        nbformat.write(nb, fout, version=4)

    print(f'Wrote {out_fname}')

if __name__ == '__main__':
    main()
    