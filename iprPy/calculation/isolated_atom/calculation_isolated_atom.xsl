<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-isolated-atom">
    <div>
      <style>
        .isolatedtable {border: 1px solid black; border-collapse: collapse;}
      </style>
      
      <xsl:variable name="calckey" select="key"/>

      <h2>Isolated atom calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/isolated_atom.html">isolated_atom</a></li>
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
      </ul>
      
      <xsl:if test="isolated-atom-energy">
      <h3>Isolated atom energies:</h3>
        <table class="isolatedtable">
          <tr class="isolatedtable">
            <th class="isolatedtable"><b>Symbol</b></th>
            <th class="isolatedtable"><b>E<sub>pot</sub> (eV)</b></th>
          </tr>
          <xsl:for-each select="isolated-atom-energy">
            <tr class="isolatedtable">
              <td class="isolatedtable"><xsl:value-of select="symbol"/></td>
              <td class="isolatedtable"><xsl:value-of select="energy/value"/></td>
            </tr>
          </xsl:for-each>
        </table>
      </xsl:if>

      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>