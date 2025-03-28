<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/TR/xhtml1/strict">
  <xsl:output method="html" encoding="utf-8" indent="yes" />
  
  <xsl:template match="calculation-stacking-fault-map-2D">
    <div>
      <style>
        .sftable {border: 1px solid black; border-collapse: collapse;}
      </style>
      
      <xsl:variable name="calckey" select="key"/>

      <h2>Stacking fault map 2D calculation results</h2>

      <ul>
        <li><b><xsl:text>UUID4: </xsl:text></b><xsl:value-of select="key"/></li>
        <li><b><xsl:text>Calculation: </xsl:text></b><a href="https://www.ctcms.nist.gov/potentials/iprPy/notebook/stacking_fault_map_2D.html">stacking_fault_map_2D</a></li>
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
        <li><b><xsl:text>Stacking Fault: </xsl:text></b>
          <xsl:choose>
            <xsl:when test="stacking-fault/URL">
              <a href="{stacking-fault/URL}"><xsl:value-of select="stacking-fault/id"/></a>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="stacking-fault/id"/>
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
        <li>
          <b><xsl:text>Minimum width perpendicular to surface setting (Angstrom): </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/minimum-width/value"/>
        </li>
        <li>
          <b><xsl:text>Number of steps along a1 vector: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/stackingfault_num_a1"/>
        </li>
        <li>
          <b><xsl:text>Number of steps along a2 vector: </xsl:text></b>
          <xsl:value-of select="calculation/run-parameter/stackingfault_num_a2"/>
        </li>
        
      </ul>

      <xsl:if test="stacking-fault-map">

        <xsl:if test="intrinsic-fault-energy">
          <ul>
            <li>
              <b><xsl:text>E</xsl:text><sub><xsl:text>ISF</xsl:text></sub><xsl:text> (mJ/m^2): </xsl:text></b>
              <xsl:value-of select="intrinsic-fault-energy/value"/>
            </li>
          </ul>
        </xsl:if> 
        <!--<h3>Stacking fault plots:</h3>
        <img src="https://potentials.nist.gov/pid/rest/local/potentials/{$calckey}-sf-2D.png" alt="2D gamma surface"/>
        <img src="https://potentials.nist.gov/pid/rest/local/potentials/{$calckey}-sf-a1.png" alt="a1 gamma plot"/>
        <img src="https://potentials.nist.gov/pid/rest/local/potentials/{$calckey}-sf-a2.png" alt="a2 gamma plot"/>-->

        <xsl:for-each select="slip-path">
          <h3><xsl:text>Slip path </xsl:text><xsl:value-of select="direction"/></h3>
          <ul>
            <li>
              <b><xsl:text>E</xsl:text><sub><xsl:text>USF</xsl:text></sub><xsl:text> minimum energy path (mJ/m^2): </xsl:text></b>
              <xsl:value-of select="unstable-fault-energy-mep/value"/>
            </li>
            <li>
              <b><xsl:text>E</xsl:text><sub><xsl:text>USF</xsl:text></sub><xsl:text> ideal path (mJ/m^2): </xsl:text></b>
              <xsl:value-of select="unstable-fault-energy-unrelaxed-path/value"/>
            </li>
            <li>
              <b><xsl:text>τ</xsl:text><sub><xsl:text>ideal</xsl:text></sub><xsl:text> minimum energy path (GPa): </xsl:text></b>
              <xsl:value-of select="ideal-shear-stress-mep/value"/>
            </li>
            <li>
              <b><xsl:text>τ</xsl:text><sub><xsl:text>ideal</xsl:text></sub><xsl:text> ideal path (GPa): </xsl:text></b>
              <xsl:value-of select="ideal-shear-stress-unrelaxed-path/value"/>
            </li> 
          </ul>
        </xsl:for-each>

        <h3>Stacking fault table:</h3>
        <table class="sftable">
          <tr class="sftable">
            <th class="sftable"><b>a<sub>1</sub> (fraction)</b></th>
            <th class="sftable"><b>a<sub>2</sub> (fraction)</b></th>
            <th class="sftable"><b>E<sub>gsf</sub> (eV/Angstrom^2)</b></th>
            <th class="sftable"><b>δ<sub>gsf</sub> (Angstrom)</b></th>
          </tr>
          <xsl:for-each select="stacking-fault-map/stacking-fault-relation/shift-vector-1-fraction">
            <xsl:variable name="row" select="position()"/>
            <tr class="sftable">
              <td class="sftable"><xsl:value-of select="."/></td>
              <td class="sftable"><xsl:value-of select="(../shift-vector-2-fraction)[$row]"/></td>
              <td class="sftable"><xsl:value-of select="(../energy/value)[$row]"/></td>
              <td class="sftable"><xsl:value-of select="(../plane-separation/value)[$row]"/></td>
            </tr>
          </xsl:for-each>
        </table>

      </xsl:if>

      <xsl:if test="error">
        <p><b><xsl:text>Error: </xsl:text></b><xsl:value-of select="error"/></p>
      </xsl:if>

    </div>

  </xsl:template>
</xsl:stylesheet>