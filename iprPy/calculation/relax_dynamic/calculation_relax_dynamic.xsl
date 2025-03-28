<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-relax-dynamic">
    <div>
      
      <xsl:variable name="calckey" select="key"/>

      <h2>Relax dynamic calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/relax_dynamic.html">relax_dynamic</a></li>
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
            <b><xsl:text>Integrator: </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/integrator"/>
          </li>
          <li>
            <b><xsl:text>Frequency of thermo outputs (steps): </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/thermosteps"/>
          </li>
          <li>
            <b><xsl:text>Frequency of dump outputs (steps): </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/dumpsteps"/>
          </li>
          <li>
            <b><xsl:text>Relaxation run length (steps): </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/runsteps"/>
          </li>
          <li>
            <b><xsl:text>Equilibration run length (steps): </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/equilsteps"/>
          </li>
          <li>
            <b><xsl:text>Random number seed: </xsl:text></b>
            <xsl:value-of select="calculation/run-parameter/randomseed"/>
          </li>
        </ul>
      </xsl:if>
        
      <xsl:if test="measured-phase-state">
        <h3>Measured phase state "mean (std)":</h3>
        <ul>
          <li>
            <b><xsl:text>Temperature (K): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/temperature/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-phase-state/temperature/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>Pressure xx (GPa): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/pressure-xx/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-phase-state/pressure-xx/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>Pressure yy (GPa): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/pressure-yy/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-phase-state/pressure-yy/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>Pressure zz (GPa): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/pressure-zz/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-phase-state/pressure-zz/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>Pressure xy (GPa): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/pressure-xy/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-phase-state/pressure-xy/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>Pressure xz (GPa): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/pressure-xz/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-phase-state/pressure-xz/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>Pressure yz (GPa): </xsl:text></b>
            <xsl:value-of select="measured-phase-state/pressure-yz/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-phase-state/pressure-yz/error"/>
            <xsl:text>)</xsl:text>
          </li>
        </ul>
      </xsl:if>

      <xsl:if test="measured-box-parameter">
        <h3>Relaxed cell "mean (std)":</h3>
        <ul>
          <li>
            <b><xsl:text>Epot (eV/atom): </xsl:text></b>
            <xsl:value-of select="cohesive-energy/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="cohesive-energy/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>Etot (eV/atom): </xsl:text></b>
            <xsl:value-of select="average-total-energy/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="average-total-energy/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>lx (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-box-parameter/lx/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-box-parameter/lx/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>ly (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-box-parameter/ly/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-box-parameter/ly/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>lz (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-box-parameter/lz/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-box-parameter/lz/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>xy (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-box-parameter/xy/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-box-parameter/xy/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>xz (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-box-parameter/xz/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-box-parameter/xz/error"/>
            <xsl:text>)</xsl:text>
          </li>
          <li>
            <b><xsl:text>yz (Angstrom): </xsl:text></b>
            <xsl:value-of select="measured-box-parameter/yz/value"/>
            <xsl:text> (</xsl:text>
            <xsl:value-of select="measured-box-parameter/yz/error"/>
            <xsl:text>)</xsl:text>
          </li>
        </ul>
      </xsl:if>

      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>