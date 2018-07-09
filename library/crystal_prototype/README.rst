===================================
crystal_prototype Reference Records
===================================

Each crystal_prototype record defines a specific crystal prototype, which can be thought of as a crystal structure stripped of the elemental information.  The file also contains metadata associated with various associated names/identifiers for the prototype, and the prototype's space group information.

Record elements
---------------

"crystal-prototype" - The root element.

- "key" - A UUID4 tag assigned to the record.

- "id" - A unique human-readable name composed from other prototype names/identifiers.  The record should be saved to a json file named by this id.

- "name" - The common name for the prototype, e.g. "body-centered cubic".

- "prototype" - The compositional prototype.  May not be unique to a given prototype.

- "Pearson-symbol" - The prototype's Pearson symbol.  May not be unique to a given prototype.

- "Strukturbericht" - The Strukturbericht symbol for the prototype.

- "space-group" - Defines space group information.

    - "number" - The space group's number.
    
    - "Hermann-Maguin" - The space group's Hermann-Maguin identifier.
    
    - "Schoenflies" - The space group's Schoenflies symbol.
    
    - "Wykoff" - Lists Wykoff information for each unique atomic site.
    
        - "letter" - The Wykoff letter for the unique atomic site.
        
        - "multiplicity" - The number of times the unique site is present in the atomic-system.
        
- "atomic-system" - An atomic-system data model for the system without element information.  These can be generated with the atomman.System.dump("system_model") method.


