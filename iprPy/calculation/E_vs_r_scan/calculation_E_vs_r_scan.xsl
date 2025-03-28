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

      <xsl:variable name="calckey" select="key"/>

      <!-- Load plotly.js into the DOM -->
      <script src='https://cdn.plot.ly/plotly-2.12.1.min.js'>//</script>
      
      <h2>E vs. r scan calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/E_vs_r_scan.html">E_vs_r_scan</a></li>
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

      <xsl:if test="cohesive-energy-relation">

        <div id='plotDiv'><!-- Plotly chart will be drawn inside this DIV --></div>
        
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

        <script>
          
          <!-- plot starting content -->
          <xsl:text>var scan = {x: [</xsl:text>
          
          <!-- Extract r values -->
          <xsl:for-each select="cohesive-energy-relation/r/value">
            <xsl:value-of select="."/>
            <xsl:if test="position() &lt; last()">
              <xsl:text>, </xsl:text>
            </xsl:if>
          </xsl:for-each>
          
          <!-- plot intermediate content -->
          <xsl:text>], y: [</xsl:text>
          
          <!-- Extract potential-energy values -->
          <xsl:for-each select="cohesive-energy-relation/cohesive-energy/value">
            <xsl:value-of select="."/>
            <xsl:if test="position() &lt; last()">
              <xsl:text>, </xsl:text>
            </xsl:if>
          </xsl:for-each>
          
          <!-- plot ending content and style info-->
          <xsl:text>], type: 'scatter'};</xsl:text>
        
          <!-- Define layout -->
          <xsl:text>var layout = {</xsl:text>
          <xsl:text>title: 'E vs r Energy Scan', </xsl:text>
          <xsl:text>xaxis: {title: 'r (Angstrom)'}, </xsl:text>
          <xsl:text>yaxis: {title: 'Potential Energy (eV/atom)'}, </xsl:text>
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