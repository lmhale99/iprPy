<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-free-energy-liquid">
    <div>
      
      <xsl:variable name="calckey" select="key"/>

      <h2>Free energy liquid calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/free_energy_liquid.html">free_energy_liquid</a></li>
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
      
      
      <xsl:if test="phase-state">
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
            <b><xsl:text>Equilibration run length (steps): </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/equilsteps"/>
          </li>
          <li>
            <b><xsl:text>Potential switching run length (steps): </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/switchsteps"/>
          </li>
          <li>
            <b><xsl:text>Reference potential p parameter: </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/p"/>
          </li>
          <li>
            <b><xsl:text>Reference potential sigma parameter: </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/sigma"/>
          </li>
          <li>
            <b><xsl:text>Random number seed: </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/randomseed"/>
          </li>
        </ul>
      </xsl:if>

      <xsl:if test="volume">
        <h3>Free energy calculation results:</h3>
        <ul>
          <li>
            <b><xsl:text>Total volume (Angstrom^3): </xsl:text></b>
            <xsl:value-of select="volume/value"/>
          </li>
          <li>
            <b><xsl:text>Number of atoms: </xsl:text></b>
            <xsl:value-of select="natoms"/>
          </li>
          <li>
            <b><xsl:text>Work of forward transformation (eV/atom): </xsl:text></b>
            <xsl:value-of select="work-forward/value"/>
          </li>
          <li>
            <b><xsl:text>Work of reverse transformation (eV/atom): </xsl:text></b>
            <xsl:value-of select="work-reverse/value"/>
          </li>
          <li>
            <b><xsl:text>Average work of transformation (eV/atom): </xsl:text></b>
            <xsl:value-of select="work/value"/>
          </li>
          <li>
            <b><xsl:text>Helmholtz free energy of reference potential (eV/atom): </xsl:text></b>
            <xsl:value-of select="Helmholtz-energy-reference/value"/>
          </li>
          <li>
            <b><xsl:text>Helmholtz free energy (eV/atom): </xsl:text></b>
            <xsl:value-of select="Helmholtz-energy/value"/>
          </li>
          <li>
            <b><xsl:text>Gibbs free energy (eV/atom): </xsl:text></b>
            <xsl:value-of select="Gibbs-energy/value"/>
          </li>
        </ul>
      </xsl:if>

      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>