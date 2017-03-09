import os

fnames = os.listdir('C:\Users\lmh1\Documents\calculations\ipr\library\calculation-dynamic-relax')

with open('calculation-dynamic-relax-names.txt', 'w') as f:
    for fname in fnames:
        if os.path.splitext(fname)[1] == '.xml':
            f.write(os.path.splitext(fname)[0] + '\n')
            
