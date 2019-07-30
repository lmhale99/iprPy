Introduction
============

The relax_box calculation style refines the lattice parameters of an
orthogonal system (crystal structure) by relaxing the box dimensions
towards a given pressure. In refining the lattice parameter values, the
box dimensions are allowed to relax, but the relative positions of the
atoms within the box are held fixed.

This calculations provides a quick tool for obtaining lattice parameters
for ideal crystal structures.

Version notes
~~~~~~~~~~~~~

-  This style was previously called refine_structure and was renamed for
   consistency with other calculations. Additionally, reporting of the
   elastic constants has been removed in favor of the separate
   elastic_constants_static style.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  With this method there is no guarantee that the resulting parameters
   are for a stable structure. Allowing internal relaxations may result
   in different values for some structures. Additionally, some
   transformation paths may be restricted from occurring due to
   symmetry, i.e. initially cubic structures may remain cubic instead of
   relaxing to a non-cubic structure.
