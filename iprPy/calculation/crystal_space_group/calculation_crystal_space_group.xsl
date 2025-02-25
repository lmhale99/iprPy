<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-crystal-space-group">
    <div>
      
      <xsl:variable name="calckey" select="key"/>

      <h2>Crystal space group calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/crystal_space_group.html">crystal_space_group</a></li>
        <li><b><xsl:text>Branch: </xsl:text></b><xsl:value-of select="calculation/branch"/></li>
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
          <b><xsl:text>Symmetry precision: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/symmetryprecision"/>
        </li>
        <li>
          <b><xsl:text>Primitive cell: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/primitivecell"/>
        </li>
        <li>
          <b><xsl:text>Ideal cell: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/idealcell"/>
        </li>
      </ul>
        
      <xsl:if test="Pearson-symbol">
        <h3>Identified space group information:</h3>
        <ul>
          <li>
            <b><xsl:text>Pearson symbol: </xsl:text></b>
            <xsl:value-of select="Pearson-symbol"/>
          </li>
          <li>
            <b><xsl:text>Space group number: </xsl:text></b>
            <xsl:value-of select="space-group/number"/>
          </li>
          <li>
            <b><xsl:text>Space group Hermann-Maguin symbol: </xsl:text></b>
            <xsl:value-of select="space-group/Hermann-Maguin"/>
          </li>
          <li>
            <b><xsl:text>Space group Schoenflies symbol: </xsl:text></b>
            <xsl:value-of select="space-group/Schoenflies"/>
          </li>
          <li>
            <b><xsl:text>Wykoff letters: </xsl:text></b>
            <xsl:value-of select="space-group/Wyckoff-fingerprint"/>
          </li>
        </ul>
      </xsl:if>

      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>