<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation_viscosity_green_kubo">
    <div>
      
      <xsl:variable name="calckey" select="key"/>

      <h2>Viscosity Green-Kubo calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/viscosity_green_kubo.html">viscosity_green_kubo</a></li>
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
            <b><xsl:text>Run length (steps): </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/runsteps"/>
          </li>
          <li>
            <b><xsl:text>Frequency of measurement output (steps): </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/outputsteps"/>
          </li>
          <li>
            <b><xsl:text>Drag coefficient: </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/dragcoeff"/>
          </li>
          <li>
            <b><xsl:text>Equilibration run length (steps): </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/equilsteps"/>
          </li>
          <li>
            <b><xsl:text>Sample interval: </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/sampleinterval"/>
          </li>
          <li>
            <b><xsl:text>Correlation length: </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/correlationlength"/>
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
            <b><xsl:text>Viscosity x-component (GPa*ps): </xsl:text></b>
            <xsl:value-of select="vx_value/value"/>
          </li>
          <li>
            <b><xsl:text>Viscosity y-component (GPa*ps): </xsl:text></b>
            <xsl:value-of select="vy_value/value"/>
          </li>
          <li>
            <b><xsl:text>Viscosity z-component (GPa*ps): </xsl:text></b>
            <xsl:value-of select="vz_value/value"/>
          </li>
          <li>
            <b><xsl:text>Viscosity mean (GPa*ps): </xsl:text></b>
            <xsl:value-of select="viscosity/value"/>
          </li>
        </ul>
      </xsl:if>

      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>