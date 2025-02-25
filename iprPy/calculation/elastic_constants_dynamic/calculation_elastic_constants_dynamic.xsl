<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-elastic-constants-dynamic">
    <div>
      <style>
        .cijtable {border: 1px solid black; border-collapse: collapse;}
      </style>

      <xsl:variable name="calckey" select="key"/>

      <h2>Elastic constants dynamic calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/elastic_constants_dynamic.html">elastic_constants_dynamic</a></li>
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
            <b><xsl:text>Temperature (K): </xsl:text></b>
            <xsl:value-of select="phase-state/temperature/value"/>
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
          <b><xsl:text>Strain range: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/strainrange"/>
        </li>
        <li>
          <b><xsl:text>Crystal symmetry normalization: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/normalized_as"/>
        </li>
        <li>
          <b><xsl:text>Equilibration run length (steps): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/equilsteps"/>
        </li>
        <li>
          <b><xsl:text>Evaluation run length (steps): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/runsteps"/>
        </li>
        <li>
          <b><xsl:text>Frequency of thermo outputs (steps): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/thermosteps"/>
        </li>
        <li>
          <b><xsl:text>Random number seed: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/randomseed"/>
        </li>
      </ul>
      
      <xsl:if test="measured-phase-state">
        <h3>Measured phase state:</h3>
        <ul>
          <li>
            <b><xsl:text>Pressure (GPa): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/pressure/value"/>
          </li>
        </ul>
      </xsl:if>

      <xsl:if test="elastic-constants">
        <h3>Cij elastic constants matrix (GPa):</h3>
        
        <table class="cijtable">
          <tr class="cijtable">
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[1]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[2]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[3]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[4]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[5]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[6]"/></td>
          </tr>
          <tr class="cijtable">
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[7]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[8]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[9]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[10]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[11]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[12]"/></td>
          </tr>
          <tr class="cijtable">
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[13]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[14]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[15]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[16]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[17]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[18]"/></td>
          </tr>
          <tr class="cijtable">
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[19]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[20]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[21]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[22]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[23]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[24]"/></td>
          </tr>
          <tr class="cijtable">
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[25]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[26]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[26]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[28]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[29]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[30]"/></td>
          </tr>
          <tr class="cijtable">
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[31]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[32]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[33]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[34]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[35]"/></td>
            <td class="cijtable"><xsl:value-of select="elastic-constants/Cij/value[36]"/></td>
          </tr>
        </table>
      </xsl:if>


      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>