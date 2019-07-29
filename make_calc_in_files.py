from pathlib import Path
import iprPy

for name, CalcClass in iprPy.calculation.loaded.items():
    calc = CalcClass()
    print(name)
    infilename = Path(calc.directory, f'calc_{name}.in')
    
    emptydict = {}
    for key in calc.allkeys:
        emptydict[key] = ''
    with open(infilename, 'w') as infile:
        infile.write(iprPy.tools.filltemplate(calc.template, emptydict, '<', '>'))
