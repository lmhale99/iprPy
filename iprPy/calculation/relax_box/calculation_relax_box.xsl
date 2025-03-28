<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-relax-box">
    <div>
      
      <xsl:variable name="calckey" select="key"/>

      <h2>Relax box calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/relax_box.html">relax_box</a></li>
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
            <b><xsl:text>Pressure xx (GPa): </xsl:text></b>
            <xsl:value-of select="phase-state/pressure-xx/value"/>
          </li>
          <li>
            <b><xsl:text>Pressure yy (GPa): </xsl:text></b>
            <xsl:value-of select="phase-state/pressure-yy/value"/>
          </li>
          <li>
            <b><xsl:text>Pressure zz (GPa): </xsl:text></b>
            <xsl:value-of select="phase-state/pressure-zz/value"/>
          </li>
          <li>
            <b><xsl:text>Pressure xy (GPa): </xsl:text></b>
            <xsl:value-of select="phase-state/pressure-xy/value"/>
          </li>
          <li>
            <b><xsl:text>Pressure xz (GPa): </xsl:text></b>
            <xsl:value-of select="phase-state/pressure-xz/value"/>
          </li>
          <li>
            <b><xsl:text>Pressure yz (GPa): </xsl:text></b>
            <xsl:value-of select="phase-state/pressure-yz/value"/>
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
            <xsl:value-of select="calculation/run-parameter/strain-range"/>
          </li>
        </ul>
      </xsl:if>
        
      <xsl:if test="measured-phase-state">
        <h3>Measured phase state:</h3>
        <ul>
          <li>
            <b><xsl:text>Temperature (K): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/temperature/value"/>
          </li>
          <li>
            <b><xsl:text>Pressure xx (GPa): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/pressure-xx/value"/>
          </li>
          <li>
            <b><xsl:text>Pressure yy (GPa): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/pressure-yy/value"/>
          </li>
          <li>
            <b><xsl:text>Pressure zz (GPa): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/pressure-zz/value"/>
          </li>
          <li>
            <b><xsl:text>Pressure xy (GPa): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/pressure-xy/value"/>
          </li>
          <li>
            <b><xsl:text>Pressure xz (GPa): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/pressure-xz/value"/>
          </li>
          <li>
            <b><xsl:text>Pressure yz (GPa): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/pressure-yz/value"/>
          </li>
        </ul>
      </xsl:if>

      <xsl:if test="measured-box-parameter">
        <h3>Relaxed cell:</h3>
        <ul>
          <li>
            <b><xsl:text>Epot (eV/atom): </xsl:text></b>
            <xsl:value-of select="cohesive-energy/value"/>
          </li>
          <li>
            <b><xsl:text>lx (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-box-parameter/lx/value"/>
          </li>
          <li>
            <b><xsl:text>ly (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-box-parameter/ly/value"/>
          </li>
          <li>
            <b><xsl:text>lz (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-box-parameter/lz/value"/>
          </li>
          <li>
            <b><xsl:text>xy (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-box-parameter/xy/value"/>
          </li>
          <li>
            <b><xsl:text>xz (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-box-parameter/xz/value"/>
          </li>
          <li>
            <b><xsl:text>yz (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-box-parameter/yz/value"/>
          </li>
        </ul>
      </xsl:if>

      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>