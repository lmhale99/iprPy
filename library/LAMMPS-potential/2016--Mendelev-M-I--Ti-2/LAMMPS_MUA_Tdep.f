!  Program to generate LAMMPS format potentials input for 
!  Mendelev-Underwood-Ackland Temperature-dependent Ti potential,
!  Compile the fortran code using, e.g. gfortran LAMMPS_MUA_Tdep.f 
!  Run the code, e.g. type ./a.out
! it will echo   "Input Temperature between 100,999K"
!  type in the required temperature.  
!  Code generates three LAMPS-compatible input 
!  files Ti1.eam.fs, Ti2.eam.fs, TiT=XXX.eam.fs
!  where XXX is the temperature you plan to simulate at (use NVT of NPT ensemble)
!  Below 100K use the Ti2 potential, above 1000K, use Ti1 
!  Bugs to: gjackland@ed.ac.uk


      program  LAMMPS_MUA_Tdep
      IMPLICIT REAL*8(A-H,O-Z)
      character*13 filename
      real*8:: bier1=0.1818, bier2=0.5099, bier3=0.2802, bier4=0.02817

! Potential parameters hardcoded later
       type potparameters
        real*8::phicor4 
        real*8:: vcut2,vcut3,vcut4,pcut
        real*8:: v14,v15,v16,v17,v18 
        real*8:: v24,v25,v26,v27,v28 
        real*8:: v34,v35,v36,v37,v38 
        real*8:: f1,f2,f3,f4,f5
        real*8::emcut1,emcut2,emcut3,emcut4,emcut5,emcut6
        real*8::splice1,splice2,splice3,splice4
        real*8:: ex0,ex1,ex2,ex3,ex4
       end  type potparameters

       type(potparameters) :: Ti1, Ti2  

!  Set parameters for Ti1 and Ti2
       call set_Ti1()
       call set_Ti2()
! Titanium specific things
       na1 = 22
       amass=47.867
       clatt=2.94653381137745
       cutoff=Ti1%vcut4  
! Temperature dependent stuff
       write(*,*)" Input Temperature between 100,999K"
       read(*,*) ITEMP
       T0=600
       Tw=100
! Ti1 is the high temperature version, Ti2 the Low T one
       GT = tanh((ITEMP-T0)/Tw)
       GT1 = (1d0+GT)/2d0
       GT2 = (1d0-GT)/2d0
       Nrho=10000
       Drho=0.03d0
       Nr=10000
       Dr=cutoff/Nr
!  LAMMPS converterlines 1,2,3 = comments (ignored)
!line 4: Nelements Element1 Element2 ... ElementN
!line 5: Nrho, drho, Nr, dr, cutoff 
!    line 1 = atomic number, mass, lattice constant, lattice type
!    embedding function F(rho) (Nrho values)
!    density function rho(r) for element 1 at element 1 (Nr values)
!    Nr values of pair potential phi(r)Â 
       write(filename,27)"TiT",ITEMP,".eam.fs"
 27    format(A3,I3,A7) 
       write(*,*)"LAMMPS potential file:",filename
       open(unit=25, file='Ti1.eam.fs')
       open(unit=26, file='Ti2.eam.fs')
       open(unit=27, file=filename) !
       write(25,*) "Potentials by Mendelev, Underwood and Ackland",
     &             " Journal of Chemical Physics 2016"
       write(25,*) "Contact information: mendelev@ameslab.gov"
       write(25,*) "Titanium potential Ti1, Temperature = High" 
       write(25,*) "1  Ti"
       write(25,*) Nrho,Drho,Nr,Dr,cutoff
       write(25,*) na1, amass, clatt, "hcp"
       write(26,*) "Potentials by Mendelev, Underwood and Ackland",
     &             " Journal of Chemical Physics 2016"
       write(26,*) "Contact information: mendelev@ameslab.gov"
       write(26,*) "Titanium potential Ti2, Temperature = Low" 
       write(26,*) "1  Ti"
       write(26,*) Nrho,Drho,Nr,Dr,cutoff
       write(26,*) na1, amass, clatt, "hcp"
       write(27,*) "Ti Sommerfeld potential",
     & " by Mendelev, Underwood and Ackland,",
     &             " Journal of Chemical Physics 2016"
       write(27,*) "Contact information: gjackland@ed.ac.uk"
       write(27,*) "Use in NVT/NPT with Temperature=",ITEMP,"K"
       write(27,*) "1  Ti"
       write(27,*) Nrho,Drho,Nr,Dr,cutoff
       write(27,*) na1, amass, clatt, "hcp"

       rad=0.0d0
       do I = 1,Nrho,5
         v1=embed(rad,Ti1)
         v1x=embed(rad,Ti2)
         rad=rad+Drho
         v2=embed(rad,Ti1)
         v2x=embed(rad,Ti2)
         rad=rad+Drho
         v3=embed(rad,Ti1)
         v3x=embed(rad,Ti2)
         rad=rad+Drho
         v4=embed(rad,Ti1)
         v4x=embed(rad,Ti2)
         rad=rad+Drho
         v5=embed(rad,Ti1)
         v5x=embed(rad,Ti2)
         rad=rad+Drho
         write(25,25)v1,v2,v3,v4,v5
         write(26,25)v1x,v2x,v3x,v4x,v5x
         write(27,25)(v1*gt1+v1x*gt2),(v2*gt1+v2x*gt2),(v3*gt1+v3x*gt2),
     &      (v4*gt1+v4x*gt2),(v5*gt1+v5x*gt2)
 25      format(5e16.8)
       enddo   
       rad=0.0d0
       do I = 1,Nr,5
         v1=phi_src(rad,Ti1)
         rad=rad+Dr
         v2=phi_src(rad,Ti1)
         rad=rad+Dr
         v3=phi_src(rad,Ti1)
         rad=rad+Dr
         v4=phi_src(rad,Ti1)
         rad=rad+Dr
         v5=phi_src(rad,Ti1)
         rad=rad+Dr
         write(25,25)v1,v2,v3,v4,v5
         write(26,25)v1,v2,v3,v4,v5
         write(27,25)v1,v2,v3,v4,v5
      enddo 
      rad=0.0d0
       do I = 1,Nr,5
         v1=vee_src(rad,Ti1)*rad
         v1x=vee_src(rad,Ti2)*rad
         rad=rad+Dr
         v2=vee_src(rad,Ti1)*rad
         v2x=vee_src(rad,Ti2)*rad
         rad=rad+Dr
         v3=vee_src(rad,Ti1)*rad
         v3x=vee_src(rad,Ti2)*rad
         rad=rad+Dr
         v4=vee_src(rad,Ti1)*rad
         v4x=vee_src(rad,Ti2)*rad
         rad=rad+Dr
         v5=vee_src(rad,Ti1)*rad
         v5x=vee_src(rad,Ti2)*rad
         rad=rad+Dr
         write(25,25)v1,v2,v3,v4,v5
         write(26,25)v1x,v2x,v3x,v4x,v5x
         write(27,25)(v1*gt1+v1x*gt2),(v2*gt1+v2x*gt2),
     &   (v3*gt1+v3x*gt2),(v4*gt1+v4x*gt2),(v5*gt1+v5x*gt2)
       enddo   
       rad=0.0
       stop
 
      contains


        function phi_src(r,pot)
        real *8 :: phi_src ! result (eV)
        real *8, intent(in) :: r ! separation (angstrom)
        type(potparameters), intent(in) :: pot
        phi_src=0.0
        if(r.lt.pot%pcut) 
     &        phi_src=pot%phicor4*exp(0.1d0*r)*(r-pot%pcut)**4
        return
        end function phi_src

  !----------------------------------------------------------------------------
  !
  ! emb_src
  !
  !----------------------------------------------------------------------------
         function embed(rhoz,pot)
         real *8 :: embed ! result (eV)
         real *8, intent(in) :: rhoz
         type(potparameters), intent(in) :: pot
         embed = -sqrt(rhoz)         
        IF(rhoz.lt.pot%emcut1)return  
        embed =  embed+pot%f1*(rhoz-pot%emcut1)**4 
        IF(rhoz.lt.pot%emcut2)return  
        embed =  embed+pot%f2*(rhoz-pot%emcut2)**4 
        IF(rhoz.lt.pot%emcut3)return  
        embed =  embed+pot%f3*(rhoz-pot%emcut3)**4 
        IF(rhoz.lt.pot%emcut4)return  
        embed =  embed+pot%f4*(rhoz-pot%emcut4)**4 
        IF(rhoz.lt.pot%emcut5)return  
        embed =  embed+pot%f5*(rhoz-pot%emcut5)**4 
c  Correction to Ti1 at extreme densities
       IF(RHOZ.gt.pot%emcut6) then
         embed=pot%ex0+pot%ex1*(rhoz-pot%emcut6)
     &      +pot%ex2*(rhoz-pot%emcut6)**2
     &      +pot%ex3*(rhoz-pot%emcut6)**3
     &      +pot%ex4*(rhoz-pot%emcut6)**4
c        embed=1.3533741622097+5.9660537422044E-01*(rhoz-pot%emcut6)
c     &      -1.4665711508917E-02*(rhoz-pot%emcut6)**2
c     &      +6.9056785356062E-04*(rhoz-pot%emcut6)**3
c     &      -3.5388769339836E-05*(rhoz-pot%emcut6)**4
       endif 
       return
       end function embed
  


  !----------------------------------------------------------------------------
  !
  ! demb_src
  !
  !----------------------------------------------------------------------------
      pure function demb_src(rhoz)
       real *8 :: demb_src ! result (eV)
       real *8, intent(in) :: rhoz
    ! Compute the embedding function derivative
       if(rhoz.gt.1.d-10) then
          demb_src = -0.5d0/sqrt(rhoz)
     & -f1*(rhoz-emcut1)**3*4*xh0(rhoz-emcut1) 
     & -f2*(rhoz-emcut2)**3*4*xh0(rhoz-emcut2) 
     & -f3*(rhoz-emcut3)**3*4*xh0(rhoz-emcut3) 
     & -f4*(rhoz-emcut4)**3*4*xh0(rhoz-emcut4) 
     & -f5*(rhoz-emcut5)**3*4*xh0(rhoz-emcut5)
       else 
          demb_src=0.0d0
       endif
       return
      end function demb_src


      function vee_src(r,pot)
      real *8 :: vee_src, x ! result (eV)
      real *8, intent(in) :: r ! separation (angstrom)
        type(potparameters), intent(in) :: pot

       VEE_SRC = 0.0d0
      IF(R.le.0.001d0) RETURN

! Biersack-Zeigler functions for titanium
      IF(R.LT.1d0) THEN
      VEE_SRC = (6.9694830017999E+03/r)*(
     &   bier1*exp(-2.7066765729847E+01*r)
     &  +bier2*exp(-7.9703166710110E+00*r)
     &  +bier3*exp(-3.4078749726736E+00*r)
     &  +bier4*exp(-1.7052062409804E+00*r))
      ELSEIF(R.LT.2.3d0) THEN
      VEE_SRC =  +exp(pot%splice1+pot%splice2*r
     &         +pot%splice3*r**2+pot%splice4*r**3)
       ELSEIF(r.lt.pot%vcut4)THEN
          VEE_SRC =   (pot%v14*(pot%vcut2-r)**4    
     &       +pot%v15*(pot%vcut2-r)**5     
     &    +pot%v16*(pot%vcut2-r)**6         
     &    +pot%v17*(pot%vcut2-r)**7         
     &    +pot%v18*(pot%vcut2-r)**8)        
     &               *xH0(pot%vcut2-r) +   
     &    (pot%v24*(pot%vcut3-r)**4         
     &    +pot%v25*(pot%vcut3-r)**5        
     &    +pot%v26*(pot%vcut3-r)**6         
     &    +pot%v27*(pot%vcut3-r)**7        
     &    +pot%v28*(pot%vcut3-r)**8)      
     &               *xH0(pot%vcut3-r) +
     &    (pot%v34*(pot%vcut4-r)**4       
     &    +pot%v35*(pot%vcut4-r)**5       
     &    +pot%v36*(pot%vcut4-r)**6       
     &    +pot%v37*(pot%vcut4-r)**7       
     &    +pot%v38*(pot%vcut4-r)**8)     
     &               *xH0(pot%vcut4-r)
       ENDIF
      return
      end function vee_src
  !----------------------------------------------------------------------------
  !
  ! Utility Function - Heaviside Step.
  !
  !----------------------------------------------------------------------------
      pure function xH0(xin)
      real *8, intent(in) :: xin ! separation (angstrom)
        real*8 :: xh0
       if(xin.lt.0.0d0)then
        xH0=0.d0
       else
        xH0=1.d0
       endif
       return
      end function xh0

      subroutine set_Ti1()
       Ti1%phicor4 =7.9483D-02
       Ti1%vcut2=3.2d0 
       Ti1%vcut3=5.4d0
       Ti1%vcut4=6.9d0
       Ti1%pcut=5.1d0
       Ti1%v14= -19.000009669827
              Ti1%v15 = +6.9503328169194
                Ti1%v16 =  +1.0141463034640E+01
               Ti1% v17=  -2.3622475018118E+01
                Ti1%v18= +8.4715024861295E+00
                Ti1%v24= +4.2964815851604E-02
                Ti1%v25= -3.1925338689760E+00
                Ti1%v26= -8.6997411310845E-01
                Ti1%v27= -1.3418235164880E+00
                Ti1%v28= -9.3059971805003E-02
                Ti1%v34= +7.8873370228139E-01
                Ti1%v35= -2.0873451358068
                Ti1%v36=  +2.0860619467995
                Ti1%v37= -9.2402710034568E-01
                Ti1%v38= +1.5279931337437E-01
       Ti1%f1=  6.4458935128222E-06
       Ti1%f2= -4.6861183499214E-05
       Ti1%f3=  1.5881962673345E-04
       Ti1%f4= -3.3153247278010E-05
       Ti1%f5= -1.0727500853945E-04

         Ti1%emcut1=18.d0
         Ti1%emcut2=22.d0
         Ti1%emcut3=26.d0
         Ti1%emcut4=28.d0
         Ti1%emcut5=30.d0
         Ti1%emcut6=50.d0

         Ti1%splice1=10.378404275169
         Ti1%splice2=-8.2358378101067
         Ti1%splice3= +3.0636189315873
         Ti1%splice4=-0.58543836194351
         Ti1%ex0=-1.3533741622097
         Ti1%ex1=+5.9660537422044E-01
         Ti1%ex2= 1.4665711508917E-02
         Ti1%ex3= -6.9056785356062E-04
         Ti1%ex4= +3.5388769339836E-05
 
      end
      subroutine set_Ti2()
       Ti2%phicor4 =7.9483D-02
       Ti2%vcut2=3.2d0 
       Ti2%vcut3=5.4d0
       Ti2%vcut4=6.9d0
       Ti2%pcut=5.1d0

                Ti2%v14= -6.4522391868171
                Ti2%v15 =-7.4406432070254
                Ti2%v16 = -1.1338596723822
                Ti2%v17=  +11.331538165644
                Ti2%v18= -8.4070436781176
                Ti2%v24= +.63252414003875
                Ti2%v25= -1.3807804217433
                Ti2%v26= +.65134886927909
                Ti2%v27= -.50882595849649
                Ti2%v28=  2.2019845067084E-02
                Ti2%v34= +5.5203429076280E-02
                Ti2%v35= -2.8338491037854E-01
                Ti2%v36= +3.3760474001764E-01
                Ti2%v37= -1.5713566606326E-01
                Ti2%v38= +2.5880555267166E-02
       Ti2%f1=  3.7224420797114E-05
       Ti2%f2= -1.4581966752354E-04
       Ti2%f3=  2.5307706881546E-04
       Ti2%f4= +1.3022021793393E-04
       Ti2%f5= -3.4570352330604E-04

         Ti2%emcut1=18.d0
         Ti2%emcut2=22.d0
         Ti2%emcut3=26.d0
         Ti2%emcut4=28.d0
         Ti2%emcut5=30.d0
         Ti2%emcut6=45.d0

         Ti2%splice1=9.2294088533131E+00
         Ti2%splice2=-5.4768063605710E+00
         Ti2%splice3= 9.9254229808463E-01
         Ti2%splice4=-1.2439775612028E-01
         Ti2%ex0=-1.3758034593242E+00
         Ti2%ex1=5.9497853813975E-01
         Ti2%ex2=7.6687260515563E-03
         Ti2%ex3=-2.0512035653105E-03
         Ti2%ex4=3.4861183325532E-04
      end
    
       end program  LAMMPS_MUA_Tdep


