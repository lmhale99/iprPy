=====================
Introduction to iprPy
=====================

Why should you use iprPy?  What will you gain by doing so?  How much extra
effort will it cost you?  Read on!

Scientific research work process
================================

Let’s imagine a young scientist who is tasked with performing a computational
investigation involving LAMMPS molecular dynamics simulations.  Here’s a
simplified description of the research process for that scientist:

1. Do a literature search for similar and relevant works.
2. Select an interatomic potential based on availability and behavior.
3. Construct atomic configurations for the investigation.
4. Perform simulations using LAMMPS.
5. Extract simulation results from the produced data.
6. Perform analysis on the extracted data.
7. Write up a publication describing the calculation methods and the processed
   results.
8. Move on to a new project.

Complications
=============

Now, let’s say a year or two goes by and someone decides to continue that
scientist’s work.  It could be the original scientist, their advisor or
boss, the next grad student or postdoc in the group, or someone from a
completely different organization.

- Can the original scientist locate all LAMMPS scripts, setup and analysis
  tools, and plotting files (Excel, Matlab, etc.) that were used?
  
- Are the located resources in a format that can easily be shared with other
  researchers?
  
- Are the resources clearly documented so that the methodology can be
  learned (or relearned)?
  
- How much content is missing and how long will it take to replace?

- Does the associated publication have enough detail that any missing
  content can be reimplemented? 
  
- Can the results of the original work be reproduced? 

- If not, can the source of the discrepancy be identified (implememtation
  error, statistical error, parameter sensitivity, invalid model, etc.)?

- Is the original data available for validation and verification of the
  original work?
  
- How easily can the original process be adapted for the new study?

All these complications lead to wasted time and money. If you develop a new
capability, you should be able to reuse that capability at any time without
having to develop it again!

It’s all in the design
======================

With iprPy, the idea is to avoid these complications beforehand through
proper calculation design. 

- Python :any:`calculation scripts <basics/calculation>` are used to collect
  specific calculation processes (steps 2-5 of the research workflow above)
  into independent, self-contained units of work. Each self-contained
  calculation allows for the entire calculation technique and knowledge behind
  the technique to be contained within a single file or folder that can easily
  be archived and/or shared.
  
- All of a calculation script’s variable parameters are read in through a
  simple :any:`input parameter <basics/inputfile>` file. This highlights the
  important parameters of the calculation allowing parameter sensitivity
  studies. The simple standard input also opens the calculations to being
  implemented into high-throughput workflow managers.
  
- Upon successful completion, the calculation scripts produce :any:`XML- or
  JSON-formatted results records <basics/recordformat>`. Records in these
  formats can automatically be uploaded to databases for storing, processing,
  and sharing of the information. Additionally, with properly named and
  structured elements, the contents of a record should be able to be
  visually interpreted by someone in the same field even if they are
  unfamiliar with the calculation.

How much extra work?
====================

Honestly, using iprPy will take some extra effort on your part (at least
initially).  But like all efforts focused on proper design, the concept is
that a little extra work now can save you from considerably more work later
on.

Much of the effort put into creating iprPy has focused on minimizing the
barriers for usage.  We want that initial cost as low as possible to reap
the rewards.

- :any:`Setup <setup>` requirements are minimal. The basic framework only
  requires Python 2.7 and a few system-independent packages.
  
- All calculation scripts can be directly executed.

- Demonstration `Jupyter Notebooks <../../demonstrations/README.md>`_ are
  provided for each calculation.

- The high-throughput tools can be directly executed from stand-alone
  scripts, called as Python functions, or accessed with :any:`inline console
  commands <highthroughput/inline>`.
  
- New :any:`calculation, record, and database styles 
  <highthroughput/classes>` can be easily added in a modular fashion.
  
- Where possible, common codebase is developed for similar calculations.