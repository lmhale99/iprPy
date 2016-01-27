!
! moldyPSI : A Fortran90/95 molecular dynamics/statics packaged based on
!            MOLDY/MDCASK (developed at LLNL) based on MPI
!
! by Peter Derlet, Paul Scherrer Institute, Switzerland (email: peter.derlet@psi.ch)
!
!************************************************************************
!
! Interatomic functions supplied by user. These functions are tabulated at the beginning
! of a simulation and therefore need not be efficiently evaluated. Any function parameters
! must be stored in the local module 'potential_params'.  
!
!************************************************************************
!                                                                                                                          
! DD Fe Potential (in development)
!
    module potential_params
    integer, save :: n_V_DD,n_phi_DD
    double precision, allocatable, dimension(:), save :: a_phi_DD,a_V_DD,r_phi_DD,r_V_DD
    double precision, save :: mu_DD,A_DD,B_DD,C_DD
    end module potential_params
!
! User supplied start routine
!
    subroutine start_potentials()
    use globals
    use potential_params
    implicit none

    integer :: i,idummy
    logical :: ldummy

    write (out_file,*) 'start_potentials(): Using Dudarev-Derlet Fe potential' 

    open (unit=10,file='fe_dd.dat')
    read (10,*) n_phi_DD,n_V_DD
    read (10,*)
    read (10,*) idummy,A_DD
    read (10,*) idummy,B_DD
    allocate (a_phi_DD(n_phi_DD),a_V_DD(n_V_DD))
    allocate (r_phi_DD(n_phi_DD),r_V_DD(n_V_DD))
    do i=1,n_phi_DD
        read (10,*) idummy,a_phi_DD(i),ldummy,r_phi_DD(i)
    end do
    do i=1,n_V_DD
        read (10,*) idummy,a_V_DD(i),ldummy,r_V_DD(i)
    end do
    close (10)

    end subroutine start_potentials
!
! User supplied finish routine
!
    subroutine finish_potentials()
    use globals
    use potential_params
    implicit none

    deallocate (a_phi_DD,a_V_DD,r_phi_DD,r_V_DD)
 
    end subroutine finish_potentials
!
! pair potential
!
    function phi_function(element_a,element_b,r)
    use potential_params
    implicit none
    integer :: element_a,element_b
    double precision :: phi_function,r
 
    integer :: i

    phi_function=0e0
    do i=1,n_V_DD
       if (r<r_V_DD(i)) phi_function=phi_function+a_V_DD(i)*(r_V_DD(i)-r)**3
    end do
 
    end function phi_function 
!
! 1st derivative of pair potential
!
    function d_phi_function(element_a,element_b,r)
    use potential_params
    implicit none
    integer :: element_a,element_b
    double precision :: d_phi_function,r
 
    integer :: i
 
    d_phi_function=0e0
    do i=1,n_V_DD
       if (r<r_V_DD(i)) d_phi_function=d_phi_function-3e0*a_V_DD(i)*(r_V_DD(i)-r)**2
    end do

    end function d_phi_function  
!
! 2nd derivative of pair potential
! 
    function dd_phi_function(element_a,element_b,r)
    use potential_params
    implicit none
    integer :: element_a,element_b
    double precision :: dd_phi_function,r
 
    integer :: i
 
    dd_phi_function=0e0
    do i=1,n_V_DD
       if (r<r_V_DD(i)) dd_phi_function=dd_phi_function+6e0*a_V_DD(i)*(r_V_DD(i)-r)
    end do
 
    end function dd_phi_function     
!
! electron pair density function
!
    function rho_function(element_a,r)
    use potential_params
    implicit none
    integer :: element_a
    double precision :: rho_function,r

    integer :: i

    rho_function=0e0
    do i=1,n_phi_DD
       if (r<r_phi_DD(i)) rho_function=rho_function+a_phi_DD(i)*(r_phi_DD(i)-r)**3
    end do
 
    end function rho_function  
!
! 1st derivative of electron pair density function
!
    function d_rho_function(element_a,r)
    use potential_params
    implicit none
    integer :: element_a
    double precision :: d_rho_function,r

    integer :: i

    d_rho_function=0e0
    do i=1,n_phi_DD
       if (r<r_phi_DD(i)) d_rho_function=d_rho_function-3e0*a_phi_DD(i)*(r_phi_DD(i)-r)**2
    end do
     
    end function d_rho_function
!
! 2nd derivative of electron pair density function 
!
    function dd_rho_function(element_a,r)
    use potential_params
    implicit none
    integer :: element_a
    double precision :: dd_rho_function,r
 
    integer :: i

    dd_rho_function=0e0
    do i=1,n_phi_DD
       if (r<r_phi_DD(i)) dd_rho_function=dd_rho_function+6e0*a_phi_DD(i)*(r_phi_DD(i)-r)
    end do
 
    end function dd_rho_function
!
! Embedding Function
! 
    function frho_function(element_a,rho)
    use potential_params
    implicit none
    integer :: element_a
    double precision :: frho_function,rho
 
    frho_function=-A_DD*sqrt(rho)
    if (rho<1e0) then
        frho_function=frho_function+(B_DD*(-1e0+sqrt(rho))*log(2e0-rho))/log(2e0)
    end if
 
    end function frho_function
!
! 1st derivative of embedding function
!  
    function d_frho_function(element_a,rho)
    use potential_params
    implicit none
    integer :: element_a
    double precision :: d_frho_function,rho
 
    d_frho_function=-A_DD/(2e0*sqrt(rho))
    if (rho<1e0) then
        d_frho_function=d_frho_function+(B_DD*(2e0*(-sqrt(rho)+rho)+(-2e0+rho)*log(2e0-rho)))/ &
            (2e0*(-2e0+rho)*sqrt(rho)*log(2e0))
    end if

    end function d_frho_function
!
! 2nd derivative of embedding function
!  
    function dd_frho_function(element_a,rho)
    use potential_params
    implicit none
    integer :: element_a
    double precision :: dd_frho_function,rho
 
    dd_frho_function=A_DD/(4e0*rho**(3e0/2e0))
    if (rho<1e0) then
        dd_frho_function=dd_frho_function-(B_DD*(-4e0*(-2e0+sqrt(rho))*rho+(-2e0+rho)**2*log(2e0-rho)))/ &
            (4e0*(-2e0+rho)**2*rho**1.5e0*log(2e0))
    end if
 
    end function dd_frho_function         
