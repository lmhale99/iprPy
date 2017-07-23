=====================
Introduction to iprPy
=====================

The iprPy framework consists of tools created to help researchers design and
run scientific calculations in a better and smarter manner. In particular,
there is built-in functionality and guiding principles that support the
development of calculations to be reproducible, reusable, adaptable, and
sharable. All data produced by the calculations is in a format that can be
easily understood and interpreted by both humans and computers. Additional
tools are included that make it possible to perform any implemented
calculation in a high-throughput manner allowing for comparative studies of
methods and models, parameter investigations, and full statistical
verifications.

Why is all of this important? A simple way to outline this is by walking
through the typical steps that a computational scientist goes through during a
molecular dynamics (MD) research project. 

1. The researcher begins by selecting appropriate interatomic potentials.
2. Atomic configurations of interest are constructed.
3. Simulations are performed using the potentials and configurations of
   interest.
4. The data is extracted from the simulation results and analyzed.
5. Models are developed to explain the data and a publication is produced.
6. The researcher moves onto a new project and all files for this work are
   archived.

The ultimate question is does this produce high-quality, meaningful results?
Answering this question requires asking a number of other questions. Why were
the particular potentials used selected? Will the results change with a
different potential? Were enough configurations used to identify true trends?
Are the results sensitive to other parameters not explored? Since MD is
deterministic, are the behaviors observed statistically reliable? Can this
work be easily validated and reproduced by other researchers?

Other questions also emerge that are of particular interest during subsequent
research projects. Can the original researcher locate and understand the
scripts and data files that they had created? Are those files and the
knowledge for using them easily transferable to other researchers, or will
they have to reconstruct the methods themselves? How easy is it to adapt the
old calculation methods to new studies? Is the data open and available, or
does it need to be reproduced as well?

The structure and tools of iprPy are meant to address most if not all of these
questions. Calculation methods are implemented in Python allowing for single
scripts to fully describe steps 2-4 described above. This makes the
calculation scripts a complete representation of the methodology. Each
calculation reads in a structured input file, and produces data in a format
that is both human and machine readable. Built-in tools are used that allow
for the interatomic potential to be easily swapped, making comparison
simulations trivial. The Python scripts can be copied into Jupyter Notebooks
allowing for full documentation of the underlying functions such that the
process can be easily learned or relearned after step 6. Finally, having the
ability to run high-throughput calculations makes it possible to investigate
if the data is meaningful and reproducible.