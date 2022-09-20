<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-E-vs-r-scan">
    <div>
      <style>
        .evsrtable {border: 1px solid black; border-collapse: collapse;}
      </style>
      
      <h1>E vs. r scan calculation results</h1>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/E_vs_r_scan.html">E_vs_r_scan</a></li>
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
        <li><b><xsl:text>Composition: </xsl:text></b><xsl:value-of select="system-info/composition"/></li>
      </ul>
      
      <xsl:if test="cohesive-energy-relation">

        <table class="evsrtable">
          <tr class="evsrtable">
            <th class="evsrtable"><b>r (Å)</b></th>
            <th class="evsrtable"><b>a (Å)</b></th>
            <th class="evsrtable"><b>E<sub>pot</sub> (eV/atom)</b></th>
          </tr>
          <xsl:for-each select="cohesive-energy-relation/r/value">
            <xsl:variable name="row" select="position()"/>
            <tr class="evsrtable">
              <td class="evsrtable"><xsl:value-of select="format-number(current(), '##0.00')"/></td>
              <td class="evsrtable"><xsl:value-of select="(../../a/value)[$row]"/></td>
              <td class="evsrtable"><xsl:value-of select="(../../cohesive-energy/value)[$row]"/></td>
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