       PROGRAM test3
	  
	   REAL Q, R_HS, ETA_HS, S_TEST
	  
	   Q = 1.
	   R_HS = 1.
	   ETA = 0.01
	  
	   S_TEST = S_HS(Q, R_HS, ETA)
	  
	   WRITE(*,*)Q, R_HS, ETA, S_TEST
	  
	   END PROGRAM
	  
	   FUNCTION S_HS(Q,RHS,ETA)
C
C      HARD SPHERE STRUCTURE FACTOR
C
C      Q= SCATTERING VECTOR
C      RHS= INTERACTION RADIUS OF HARD SPHERES
C      ETA= VOLUME FRACTION OF HARD SPHERES
C
C
       ALN=(1.-ETA)**4.
       AL=(1.+2.*ETA)**2./ALN
       BE=-6.*ETA*(1.+0.5*ETA)**2./ALN
       GA=0.5*ETA*AL
C
       AR=2.*RHS*Q
C
C      LOW ARGUMENT EXPANSION
C
       IF(AR.LT.0.4)THEN

         GG=AL*(1./3.-AR*AR/30.)+BE*(1./4.-AR*AR/36.)
     !      +GA*(1./6-AR*AR/48.)

       ELSE
         SA=SIN(AR)
         CA=COS(AR)
         GG=AL*(SA-AR*CA)/AR**3.
     !     +BE*(2.*AR*SA+(2.-AR**2.)*CA-2.)/AR**4.
     !     +GA*(-AR**4.*CA+4.*((3.*AR**2.-6.)*CA+(AR**3.-6.*AR)
     !     *SA+6.))/AR**6.
       END IF

       S_HS=1. / (1.+24.*ETA*GG)
       RETURN
       END
	  
