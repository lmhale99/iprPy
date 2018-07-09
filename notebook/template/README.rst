==========================
Template Jupyter Notebooks
==========================

To make it easier to ensure 1:1 correspondence of the content in the Jupyter demonstration Notebooks and the corresponding calculation folders, a template Jupyter Notebook can be defined for each calculation.

1. The template Notebooks are named after their corresponding calculation styles and placed in the notebook/template directory.

2. The location in the Jupyter template where documentation file content or calculation script functions is to be placed is marked by delimited text
   
   - The leading delimiter is ^fill^.
   
   - The trailing delimiter is ^here^.
   
   - The full contents of a file will be added if the filename is given 
     between the delimiters:
        
        ^fill^README.md^here^
     
   - The Python code for a specific function will be added if the filename
     followed by the function name in parenthesis is added:
        
        ^fill^calc.py(main)^here^

3. The build_Notebooks.py script will replace the delimited text with the corresponding content and save the complete Notebook in the notebook directory.

4. After building, check that the Notebooks work.  Make any changes to the source content in the calculation files or in the template Notebooks and run build_Notebooks.py again.  If you make changes to the generated Notebooks themselves, the changes will be lost if the build script is called.