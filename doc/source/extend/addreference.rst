=================
Reference Library
=================

A number of reference records can be found in the iprPy/library directory.
These collect together metadata and data associated with meaningful parameter
sets that can then be used as inputs for the calculations.  The reference
records in the library directory are collected together in subdirectories based
on their record styles.

New reference records for an existing style can simply be added to the
iprPy/library directory.  The references are stored in JSON format meaning that
you can investigate their design using a text editor.  One easy way to add
additional records is to copy one of the existing records of a given style,
then change the values in the copy.

While each record style is different, they all start in the same way

- Each style has a single root element indicative of the record style.

- The first element within the root is **key**, a UUID4 identifier unique to
  each record.

- The second element within the root is **id**, a human-readable identifier
  unique to the record style and ideally unique across all records.  The
  record's file name must match the record's id.

See the description of a given record style to learn more about the other
elements that it contains.

After adding any new references to the library, remember to copy them to any
databases using build_ref.

New types of reference records can be added by defining a new record style,
then adding records to the library in the corresponding subdirectory.
