<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-diatom-scan">
    <div>
      <style>
        .diatomtable {border: 1px solid black; border-collapse: collapse;}
      </style>

      <!-- Load plotly.js into the DOM -->
      <script src='https://cdn.plot.ly/plotly-2.12.1.min.js'>//</script>
      
      <h1>Diatom scan calculation results</h1>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/diatom_scan.html">diatom_scan</a></li>
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
      
      <xsl:if test="diatom-energy-relation">

        <div id='plotDiv'><!-- Plotly chart will be drawn inside this DIV --></div>
        
        <table class="diatomtable">
          <tr class="diatomtable">
            <th class="diatomtable"><b>r (Å)</b></th>
            <th class="diatomtable"><b>E<sub>pot</sub> (eV)</b></th>
          </tr>
          <xsl:for-each select="diatom-energy-relation/r/value">
            <xsl:variable name="row" select="position()"/>
            <tr class="diatomtable">
              <td class="diatomtable"><xsl:value-of select="format-number(current(), '##0.00')"/></td>
              <td class="diatomtable"><xsl:value-of select="(../../potential-energy/value)[$row]"/></td>
            </tr>
          </xsl:for-each>
        </table>

        <script>
          
          <!-- plot starting content -->
          <xsl:text>var scan = {x: [</xsl:text>
          
          <!-- Extract r values -->
          <xsl:for-each select="diatom-energy-relation/r/value">
            <xsl:value-of select="."/>
            <xsl:if test="position() &lt; last()">
              <xsl:text>, </xsl:text>
            </xsl:if>
          </xsl:for-each>
          
          <!-- plot intermediate content -->
          <xsl:text>], y: [</xsl:text>
          
          <!-- Extract potential-energy values -->
          <xsl:for-each select="diatom-energy-relation/potential-energy/value">
            <xsl:value-of select="."/>
            <xsl:if test="position() &lt; last()">
              <xsl:text>, </xsl:text>
            </xsl:if>
          </xsl:for-each>
          
          <!-- plot ending content and style info-->
          <xsl:text>], type: 'scatter'};</xsl:text>
        
          <!-- Define layout -->
          <xsl:text>var layout = {</xsl:text>
          <xsl:text>title: 'Diatom Energy Scan', </xsl:text>
          <xsl:text>xaxis: {title: 'r (Angstrom)'}, </xsl:text>
          <xsl:text>yaxis: {title: 'Potential Energy (eV)'}, </xsl:text>
          <xsl:text>width: 1000, </xsl:text>
          <xsl:text>height: 700</xsl:text>
          <xsl:text>};</xsl:text>
        
          <!-- Create plot -->
          <xsl:text>var data = [scan]; Plotly.newPlot('plotDiv', data, layout);</xsl:text>
        
        </script>
      </xsl:if>

      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>