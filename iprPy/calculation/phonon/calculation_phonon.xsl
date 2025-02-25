<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-phonon">
    <div>
      <style>
        .cijtable {border: 1px solid black; border-collapse: collapse;}
      </style>

      <xsl:variable name="calckey" select="key"/>

      <h2>Phonon calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/phonon.html">phonon</a></li>
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
          <b><xsl:text>Atomic displacement distance (Angstrom): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/displacementdistance/value"/>
        </li>
        <li>
          <b><xsl:text>Symmetry precision tolerance: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/symmetryprecision"/>
        </li>
        <li>
          <b><xsl:text>Strain range: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/strainrange"/>
        </li>
        <li>
          <b><xsl:text>Number of strains used for QHA: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/numstrains"/>
        </li>
      </ul>

      <xsl:if test="not(status)">
        <h3>Phonon plots:</h3>
        <img src="https://potentials.nist.gov/pid/rest/local/potentials/{$calckey}-band.png" alt="band structure"/>
        <img src="https://potentials.nist.gov/pid/rest/local/potentials/{$calckey}-dos.png" alt="density of states"/>
        <img src="https://potentials.nist.gov/pid/rest/local/potentials/{$calckey}-pdos.png" alt="partial density of states"/>
        <xsl:if test="volume-scan">
          <img src="https://potentials.nist.gov/pid/rest/local/potentials/{$calckey}-bmod.png" alt="volumetric scan for B"/>
          <img src="https://potentials.nist.gov/pid/rest/local/potentials/{$calckey}-helmvol.png" alt="Helmholtz volumetric scan"/>
        </xsl:if>
        
      </xsl:if>

      <xsl:if test="volume-scan">
        <h3>Volumetric scan properties:</h3>
        <ul>
          <li>
            <b><xsl:text>E0 (eV/atom): </xsl:text></b>
            <xsl:value-of select="E0/value"/>
          </li>
          <li>
            <b><xsl:text>B0 (GPa): </xsl:text></b>
            <xsl:value-of select="B0/value"/>
          </li>
          <li>
            <b><xsl:text>B0' (GPa): </xsl:text></b>
            <xsl:value-of select="B0prime/value"/>
          </li>
          <li>
            <b><xsl:text>V0 (Angstrom^3): </xsl:text></b>
            <xsl:value-of select="V0/value"/>
          </li>
        </ul>        
      </xsl:if>


      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>