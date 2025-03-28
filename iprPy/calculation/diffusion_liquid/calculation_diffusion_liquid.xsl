<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation_diffusion_liquid">
    <div>
      
      <xsl:variable name="calckey" select="key"/>

      <h2>Diffusion liquid calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/diffusion_liquid.html">diffusion_liquid</a></li>
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
      
      
      <xsl:if test="phase-state">
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
            <b><xsl:text>Timestep (ps): </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/timestep/value"/>
          </li>
          <li>
            <b><xsl:text>Run length per simulation (steps): </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/runsteps"/>
          </li>
          <li>
            <b><xsl:text>Number of simulations: </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/simruns"/>
          </li>
          <li>
            <b><xsl:text>Equilibration run length (steps): </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/equilsteps"/>
          </li>
        </ul>
      </xsl:if>

      <xsl:if test="measured_temperature">
        <h3>Diffusion calculation results:</h3>
        <ul>
          <li>
            <b><xsl:text>Measured mean temperature (K): </xsl:text></b>
            <xsl:value-of select="measured_temperature/value"/>
          </li>
          <li>
            <b><xsl:text>Diffusion constant from cumulative MSD (m^2/s): </xsl:text></b>
            <xsl:value-of select="diffusion_msd_long/value"/>
          </li>
          <li>
            <b><xsl:text>Diffusion constant from mean MSD (m^2/s): </xsl:text></b>
            <xsl:value-of select="diffusion_msd_short/value"/>
          </li>
          <li>
            <b><xsl:text>Diffusion constant from VACF (m^2/s): </xsl:text></b>
            <xsl:value-of select="diffusion_vacf/value"/>
          </li>
        </ul>
      </xsl:if>

      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>