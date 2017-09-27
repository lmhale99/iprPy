from __future__ import print_function, division, absolute_import
import os
import pypandoc

for htmlroot, htmldirs, htmlfiles in os.walk('html'):
    rstroot = htmlroot.replace('html', 'test', 1)
    if not os.path.isdir(rstroot):
        os.makedirs(rstroot)
        
    for htmlfile in htmlfiles:
        name, ext = os.path.splitext(htmlfile)
        if ext == '.html':
            infile = os.path.join(htmlroot,htmlfile)
            outfile = os.path.join(rstroot, name+'.md')
            with open(outfile, 'w') as fo:
                with open(infile) as fi:
                    fo.write(pypandoc.convert_text(fi.read(), 'md', format='html'))
            