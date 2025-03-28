<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-relax-liquid">
    <div>
      
      <xsl:variable name="calckey" select="key"/>

      <h2>Relax liquid calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/relax_liquid_redo.html">relax_liquid_redo</a></li>
        <li><b><xsl:text>Branch: </xsl:text></b><xsl:value-of select="calculation/branch"/></li>
        <li><b><xsl:text>Potential: </xsl:text></b>
          <xsl:choose>
            <xsl:when test="potential-LAMMPS/potential/URL">
              <a href="{potential-LAMMPS/potential/URL}"><xsl:value-of select="potential-LAMMPS/potential/id"/></a>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="potential-LAMMPS/potential/id"/>
            </xsl:otherwise>
          </xsl:choose>
        </li>
        <li><b><xsl:text>LAMMPS implementation: </xsl:text></b>
          <xsl:choose>
            <xsl:when test="potential-LAMMPS/URL">
              <a href="{potential-LAMMPS/URL}"><xsl:value-of select="potential-LAMMPS/id"/></a>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="potential-LAMMPS/id"/>
            </xsl:otherwise>
          </xsl:choose>
        </li>
        <li><b><xsl:text>Family: </xsl:text></b>
          <xsl:choose>
            <xsl:when test="system-info/family-URL">
              <a href="{system-info/family-URL}"><xsl:value-of select="system-info/family"/></a>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="system-info/family"/>
            </xsl:otherwise>
          </xsl:choose>
        </li>
        <xsl:if test="system-info/parent">
          <li><b><xsl:text>Parent record: </xsl:text></b>
            <xsl:choose>
              <xsl:when test="system-info/parent-URL">
                <a href="{system-info/parent-URL}"><xsl:value-of select="system-info/parent"/></a>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="system-info/parent"/>
              </xsl:otherwise>
            </xsl:choose>
          </li>
        </xsl:if>
        <li><b><xsl:text>Composition: </xsl:text></b><xsl:value-of select="system-info/composition"/></li>
      </ul>
      
      
      
      <h3>Calculation parameters:</h3>
      <ul>
        <li>
          <b><xsl:text>Temperature (K): </xsl:text></b>
          <xsl:value-of select="phase-state/temperature/value"/>
        </li>
        <li>
          <b><xsl:text>Pressure (GPa): </xsl:text></b>
          <xsl:value-of select="phase-state/pressure/value"/>
        </li>
        <li>
          <b><xsl:text>Cell size multipliers: </xsl:text></b>
          <xsl:text>(</xsl:text>
          <xsl:value-of select="calculation/run-parameter/size-multipliers/a[1]"/>
          <xsl:text>, </xsl:text>
          <xsl:value-of select="calculation/run-parameter/size-multipliers/a[2]"/>
          <xsl:text>), (</xsl:text>
          <xsl:value-of select="calculation/run-parameter/size-multipliers/b[1]"/>
          <xsl:text>, </xsl:text>
          <xsl:value-of select="calculation/run-parameter/size-multipliers/b[2]"/>
          <xsl:text>), (</xsl:text>
          <xsl:value-of select="calculation/run-parameter/size-multipliers/c[1]"/>
          <xsl:text>, </xsl:text>
          <xsl:value-of select="calculation/run-parameter/size-multipliers/c[2]"/>
          <xsl:text>)</xsl:text>
        </li>
        <li>
          <b><xsl:text>Temperature for the melting stage(K): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/temperature_melt"/>
        </li>
        <li>
          <b><xsl:text>Melting stage run length (steps): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/meltsteps"/>
        </li>
        <li>
          <b><xsl:text>Cooling stage run length (steps): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/coolsteps"/>
        </li>
        <li>
          <b><xsl:text>Volume equilibration run length (steps): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/equilvolumesteps"/>
        </li>
        <li>
          <b><xsl:text>Number of samples taken during volume equilibration run: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/equilvolumesamples"/>
        </li>
        <li>
          <b><xsl:text>Evaluation run length (steps): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/runsteps"/>
        </li>
        <li>
          <b><xsl:text>Frequency of dump file generation (steps): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/dumpsteps"/>
        </li>
        <li>
          <b><xsl:text>Create new atomic velocities: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/createvelocities"/>
        </li>
        <li>
          <b><xsl:text>Number of RDF bins: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/rdf_nbins"/>
        </li>
        <li>
          <b><xsl:text>Minimum r coordinate for RDF measurement: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/rdf_minr/value"/>
        </li>
        <li>
          <b><xsl:text>Maximum r coordinate for RDF measurement: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/rdf_maxr/value"/>
        </li>
        <li>
          <b><xsl:text>Random number seed: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/randomseed"/>
        </li>
      </ul>
        
      <xsl:if test="measured-phase-state">
        <h3>Measured phase state "mean (std)":</h3>
        <ul>
          <li>
            <b><xsl:text>Temperature (K): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/temperature/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-phase-state/temperature/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>Pressure (GPa): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/pressure/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-phase-state/pressure/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>Volume (angstrom^3/atom): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/volume/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-phase-state/volume/error"/>
            <xsl:text>)</xsl:text>
          </li>
        </ul>
      </xsl:if>

      <xsl:if test="total-energy-per-atom">
        <h3>Relaxed cell "mean (std)":</h3>
        <ul>
          <li>
            <b><xsl:text>Epot (eV/atom): </xsl:text></b>
            <xsl:value-of select="potential-energy-per-atom/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="potential-energy-per-atom/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>Etot (eV/atom): </xsl:text></b>
            <xsl:value-of select="total-energy-per-atom/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="total-energy-per-atom/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>lx (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/lx/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-phase-state/lx/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>ly (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/ly/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-phase-state/ly/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>lz (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/lz/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-phase-state/lz/error"/>
            <xsl:text>)</xsl:text>
          </li>
        </ul>
      </xsl:if>

      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>