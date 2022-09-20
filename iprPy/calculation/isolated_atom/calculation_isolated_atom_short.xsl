<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-isolated-atom">
    <div>
      <xsl:text>calculation_isolated_atom record for </xsl:text>
      <xsl:value-of select="potential-LAMMPS/id"/>
    </div>

  </xsl:template>
</xsl:stylesheet>