point_defect_diffusion calculation style
========================================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Description updated: 2019-07-26

Introduction
------------

The point_defect_diffusion calculation style estimates the diffusion
rate of a point defect at a specified temperature. A system is created
with a single point defect, and subjected to a long time molecular
dynamics simulation. The mean square displacement for the defect is
computed, and used to estimate the diffusion constant.

Version notes
~~~~~~~~~~~~~

-  2022-03-11: Notebook updated to reflect version 0.11.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  The calculation estimates the defect’s diffusion by computing the
   mean square displacement of all atoms in the system. This is useful
   for estimating rates associated with vacancies and self-interstitials
   as the process is not confined to a single atom’s motion. However,
   this makes the calculation ill-suited to measuring diffusion of
   substitutional impurities as it does not individually track each
   atom’s position throughout.

Method and Theory
-----------------

First, a defect system is constructed by adding a single point defect
(or defect cluster) to an initially bulk system using the
atomman.defect.point() function.

A LAMMPS simulation is then performed on the defect system. The
simulation consists of two separate runs

1. NVT equilibrium run: The system is allowed to equilibrate at the
   given temperature using nvt integration.

2. NVE measurement run: The system is then evolved using nve
   integration, and the total mean square displacement of all atoms is
   measured as a function of time.

Between the two runs, the atomic velocities are scaled such that the
average temperature of the nve run is closer to the target temperature.

The mean square displacement of the defect,
:math:`\left< \Delta r_{ptd}^2 \right>` is then estimated using the mean
square displacement of the atoms :math:`\left< \Delta r_{i}^2 \right>`.
Under the assumption that all diffusion is associated with the single
point defect, the defect’s mean square displacement can be taken as the
summed square displacement of the atoms

.. math::  \left< \Delta r_{ptd}^2 \right> \approx \sum_i^N \Delta r_{i}^2 = N \left< \Delta r_{i}^2 \right>, 

where :math:`N` is the number of atoms in the system. The diffusion
constant is then estimated by linearly fitting the change in mean square
displacement with time

.. math::  \left< \Delta r_{ptd}^2 \right> = 2 d D_{ptd} \Delta t, 

where d is the number of dimensions included.
