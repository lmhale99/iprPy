<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-dislocation-monopole">
    <div>
      <style>
        .kijtable {border: 1px solid black; border-collapse: collapse;}
      </style>
      
      <xsl:variable name="calckey" select="key"/>

      <h2>Dislocation monopole calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/dislocation_monopole.html">dislocation_monopole</a></li>
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
        <li><b><xsl:text>Dislocation type: </xsl:text></b>
          <xsl:choose>
            <xsl:when test="dislocation/URL">
              <a href="{dislocation/URL}"><xsl:value-of select="dislocation/id"/></a>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="dislocation/id"/>
            </xsl:otherwise>
          </xsl:choose>
        </li>
      </ul>
      
      
      <xsl:if test="base-system">
        <h3>Core structure plots:</h3>
        <img src="https://potentials.nist.gov/pid/rest/local/potentials/{$calckey}-nye-dd.png" alt="Nye tensor + differential displacement plot"/>

        <h3>Downloadable atomic configuration files:</h3>
        <ul>
          <li>
            <b><xsl:text>Reference system: </xsl:text></b>
            <a href="https://potentials.nist.gov/pid/rest/local/potentials/{$calckey}-base.dump"><xsl:text>base.dump</xsl:text></a>
          </li>
          <li>
            <b><xsl:text>Dislocation system: </xsl:text></b>
            <a href="https://potentials.nist.gov/pid/rest/local/potentials/{$calckey}-disl.dump"><xsl:text>disl.dump</xsl:text></a>
          </li>
        </ul>
      </xsl:if>


        

      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>