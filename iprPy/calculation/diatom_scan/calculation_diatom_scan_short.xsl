<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-diatom-scan">
    <div>
      
      <h2>Diatom scan calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/diatom_scan.html">diatom_scan</a></li>
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
        <li><b><xsl:text>Symbol(s): </xsl:text></b>
          <xsl:for-each select="system-info/symbol">
            <xsl:value-of select="."/>
            <xsl:if test="position() &lt; last()">
              <xsl:text>-</xsl:text>
            </xsl:if>
          </xsl:for-each>
        </li>
      </ul>
      
      <h3>Calculation parameters:</h3>
      <ul>
        <li>
          <b><xsl:text>Minimum r (Angstrom): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/minimum_r/value"/>
        </li>
        <li>
          <b><xsl:text>Maximum r (Angstrom): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/maximum_r/value"/>
        </li>
        <li>
          <b><xsl:text>Number of r measurements: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/number_of_steps_r"/>
        </li>
      </ul>

      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>