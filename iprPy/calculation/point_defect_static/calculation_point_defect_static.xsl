<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-point-defect-static">
    <div>
      
      <xsl:variable name="calckey" select="key"/>

      <h2>Point defect static calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/point_defect_static.html">point_defect_static</a></li>
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
        <li><b><xsl:text>Point defect: </xsl:text></b>
          <xsl:choose>
            <xsl:when test="point-defect/URL">
              <a href="{point-defect/URL}"><xsl:value-of select="point-defect/id"/></a>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="point-defect/id"/>
            </xsl:otherwise>
          </xsl:choose>
        </li>
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
          <b><xsl:text>Minimization energy tolerance: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/energytolerance"/>
        </li>
        <li>
          <b><xsl:text>Minimization force tolerance (eV/Angstrom): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/forcetolerance/value"/>
        </li>
        <li>
          <b><xsl:text>Max number of minimization iterations: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/maxiterations"/>
        </li>
        <li>
          <b><xsl:text>Max number of minimization evaluations: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/maxevaluations"/>
        </li>
        <li>
          <b><xsl:text>Max atomic relaxation distance per iteration (Angstrom): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/maxatommotion/value"/>
        </li>
      </ul>

      <xsl:if test="cohesive-energy">
        <h3>Point defect properties:</h3>
        <ul>
          <li>
            <b><xsl:text>Bulk potential energy (eV/atom): </xsl:text></b>
            <xsl:value-of select="cohesive-energy/value"/>
          </li>
          <li>
            <b><xsl:text>Number of atoms: </xsl:text></b>
            <xsl:value-of select="number-of-atoms"/>
          </li>
          <li>
            <b><xsl:text>Defect formation energy (eV): </xsl:text></b>
            <xsl:value-of select="defect-formation-energy/value"/>
          </li>
          <li>
            <b><xsl:text>Elastic dipole tensor p</xsl:text><sub><xsl:text>11</xsl:text></sub><xsl:text> (eV): </xsl:text></b>
            <xsl:value-of select="defect-elastic-dipole-tensor/value[1]"/>
          </li>
          <li>
            <b><xsl:text>Elastic dipole tensor p</xsl:text><sub><xsl:text>22</xsl:text></sub><xsl:text> (eV): </xsl:text></b>
            <xsl:value-of select="defect-elastic-dipole-tensor/value[5]"/>
          </li>
          <li>
            <b><xsl:text>Elastic dipole tensor p</xsl:text><sub><xsl:text>33</xsl:text></sub><xsl:text> (eV): </xsl:text></b>
            <xsl:value-of select="defect-elastic-dipole-tensor/value[9]"/>
          </li>
          <li>
            <b><xsl:text>Elastic dipole tensor p</xsl:text><sub><xsl:text>12</xsl:text></sub><xsl:text> (eV): </xsl:text></b>
            <xsl:value-of select="defect-elastic-dipole-tensor/value[2]"/>
          </li>
          <li>
            <b><xsl:text>Elastic dipole tensor p</xsl:text><sub><xsl:text>13</xsl:text></sub><xsl:text> (eV): </xsl:text></b>
            <xsl:value-of select="defect-elastic-dipole-tensor/value[3]"/>
          </li>
          <li>
            <b><xsl:text>Elastic dipole tensor p</xsl:text><sub><xsl:text>23</xsl:text></sub><xsl:text> (eV): </xsl:text></b>
            <xsl:value-of select="defect-elastic-dipole-tensor/value[6]"/>
          </li>
          <li>
            <b><xsl:text>Has defect reconfigured?: </xsl:text></b>
            <xsl:value-of select="reconfiguration-check/has_reconfigured"/>
          </li>
          <xsl:if test="reconfiguration-check/centrosummation">
            <li>
              <b><xsl:text>Defect centrosummation check: </xsl:text></b>
              <xsl:text>[</xsl:text>
              <xsl:value-of select="reconfiguration-check/centrosummation[1]"/>
              <xsl:text>, </xsl:text>
              <xsl:value-of select="reconfiguration-check/centrosummation[2]"/>
              <xsl:text>, </xsl:text>
              <xsl:value-of select="reconfiguration-check/centrosummation[3]"/>
              <xsl:text>]</xsl:text>
            </li>
          </xsl:if>
          <xsl:if test="reconfiguration-check/position_shift">
            <li>
              <b><xsl:text>Change in defect atom position check: </xsl:text></b>
              <xsl:text>[</xsl:text>
              <xsl:value-of select="reconfiguration-check/position_shift[1]"/>
              <xsl:text>, </xsl:text>
              <xsl:value-of select="reconfiguration-check/position_shift[2]"/>
              <xsl:text>, </xsl:text>
              <xsl:value-of select="reconfiguration-check/position_shift[3]"/>
              <xsl:text>]</xsl:text>
            </li>
          </xsl:if>
          <xsl:if test="reconfiguration-check/db_vect_shift">
            <li>
              <b><xsl:text>Change in dumbbell vector check: </xsl:text></b>
              <xsl:text>[</xsl:text>
              <xsl:value-of select="reconfiguration-check/db_vect_shift[1]"/>
              <xsl:text>, </xsl:text>
              <xsl:value-of select="reconfiguration-check/db_vect_shift[2]"/>
              <xsl:text>, </xsl:text>
              <xsl:value-of select="reconfiguration-check/db_vect_shift[3]"/>
              <xsl:text>]</xsl:text>
            </li>
          </xsl:if>
        </ul>
      </xsl:if>

      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>