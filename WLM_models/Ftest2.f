C	  Compiled using gfortran.
	  PROGRAM test2
	  
C	  functions present in this program:
C	  S_KP_EXV(Q, RL, RLL)
C	  FI(X)
C	  SI(X)
C     S_EXV_APP(Q)

	  REAL Q, RL, RLL, FITEST, SITEST, EXVTEST, KPTEST
	  DIMENSION A1(1:6)
	  A1(1) = 0.05
	  A1(2) = 0.5
	  A1(3) = 1.0
	  A1(4) = 5.0
	  A1(5) = 10.0
	  
	  Q = 1.
	  RL = 1.
	  RLL = 1.
	  FITEST = FI(Q)
	  SITEST = SI(1.)
	  EXVTEST = S_EXV_APP(1.)
	  KPTEST = S_KP_EXV(Q,RL,RLL)
      DO I = 1,5
	     SITEST = SI(A1(I))
		 WRITE(*,*)I, A1(I), SITEST
	  END DO
C	  WRITE(*,*)'FI', Q, '=', FITEST
C	  WRITE(*,*)'Q, RL, RLL, FITEST, SITEST, EXVTEST, KPTEST' 
C	  WRITE(*,*)Q,RL,RLL,FITEST,SITEST,EXVTEST,KPTEST
      
	  STOP
	  END
	  
	   FUNCTION S_KP_EXV(Q,RL,RLL)

C      RL= CONTOUR LENGTH
C      RRL = KUHN LENGTH
C              * THAT IS RLL  IS THE STATISTICLA SEGMENT LENGTH
C      I_EXVOL = 0 : GAUSSIAN COILS
C                1 : EXCLUDED VOLUME EFFECTS INCLUDED
C
C
      DIMENSION A1(2:5,0:2),A2(2:5,1:2),B1(0:2,0:2),B2(0:2,1:2)
      DIMENSION AA(2:5),BB(0:2)
      REAL K,L,K_MEM

      DATA A1,A2,B1,B2/-0.1222,0.3051,-0.0711,0.0584,1.761,2.252,
     $ -1.291,0.6994,-26.04,20.00,4.382,1.594,0.1212,-0.4169,0.1988,
     $ 0.3435,0.0170,-0.4731,0.1869,0.3350,-0.0699,-0.0900,0.2677,
     $ 0.1342,0.0138,0.1898,-0.2020,-0.0114,0.0123,-0.5171,-0.2028,
     $ -0.3112,0.6950,-0.3238,-0.5403/



      DATA PI /3.1415927/
C

C
C     DIMENSIONLESS UNITS
C
      K=Q*RLL
      L=RL/RLL
C      WRITE(*,*)RL,RLL,L



      I_EXVOL=1
      SCALE=1.

      KK=0
      IF(K.GT.10.)THEN
        K_MEM=K
        K=10.
        KK=1
      END IF

C
C     R_G^2 OF DEBYE func
C

      IF(I_EXVOL.EQ.0)THEN
      AEXP=2.*L
      IF(AEXP.GT. 74.)THEN
         AEXP=0.
        ELSE
         AEXP=EXP(-AEXP)
      END IF
      S2=L/6.-0.25+0.25/L-(1.-AEXP)/(8.*L*L)
C
C     DEBYE func
C
      U=S2*K*K
      AEXP=U
      IF(AEXP.GT. 74.)THEN
         AEXP=0.
        ELSE
         AEXP=EXP(-AEXP)
      END IF
      IF(U.LT.0.01)THEN
        F_DEBYE=1.-0.333333333*U
      ELSE
        F_DEBYE=2.*(AEXP+U-1.)/U**2
      END IF
C
C     EXCLUDED VOLUME EFFECTS
C
      ELSE

      AEXP=2.*L
      IF(AEXP.GT. 60.)THEN
         AEXP=0.
        ELSE
         AEXP=EXP(-AEXP)
      END IF

       EPSI=0.17
       EXPAN=(1.+ABS(L/3.12)**2.+ABS(L/8.67)**3.)**(EPSI/3.)
       S2=L/6.-0.25+0.25/L-(1.-AEXP)/(8.*L*L)
       S2=S2*EXPAN

C       WRITE(*,*)' RG = ', SQRT(S2)
C       WRITE(*,*)' EXP= ', SQRT(EXPAN)

       F_DEBYE=S_EXV_APP(K*SQRT(S2))
      END IF


C
C     ROD SCATTERING func
C
      A=K*L
      F_ROD=2.*SI(A)/A-4./A**2*(SIN(0.5*A))**2
C
C     WEIGHT CHI
C
      IF(I_EXVOL.EQ.0)THEN
        PSI=PI*S2*K/(2.*L)
      ELSE
      PSI=K*(PI/ABS(1.103*L))**1.5*S2**1.282
      END IF
      AEXP=1./PSI**5
      IF(AEXP.GT. 74.)THEN
         CHI=0.
        ELSE
         CHI=EXP(-AEXP)
      END IF
C
C     INTERPOLATED func
C

        F_IP=(1.-CHI)*F_DEBYE+CHI*F_ROD
C
C     CORRECTION func FGAMMA
C
C     CALCULATE A'S
C
           AEXP=40./(4.*L)
           IF(AEXP.GT. 74.)THEN
             AEXP=0.
           ELSE
            AEXP=EXP(-AEXP)
           END IF
           AEXP1=2.*L
           IF(AEXP1.GT. 74.)THEN
             AEXP1=0.
           ELSE
            AEXP1=EXP(-AEXP1)
           END IF

      DO I=2,5
        AA(I)=0.
          DO II=0,2
           IF(II.EQ.0)THEN
             AA(I)=AA(I)+A1(I,II)/(L**II)*AEXP
           ELSE
             AA(I)=AA(I)+A1(I,II)/(L**II)*AEXP+A2(I,II)*(L**II)*AEXP1
           END IF
         END DO
      END DO
C
C     CALULATE B'S
C
      DO I=0,2
        BB(I)=0.
          DO II=0,2
           IF(II.EQ.0)THEN
             BB(I)=BB(I)+B1(I,II)/L**II
           ELSE
             BB(I)=BB(I)+B1(I,II)/L**II+B2(I,II)*L**II*AEXP1
           END IF
         END DO
      END DO
C
C     CALCULATE FGAMMA
C
      F1=0.
      F2=0.
      DO I=2,5
        F1=F1+AA(I)*PSI**I
      END DO
      DO I=0,2
        F2=F2+BB(I)/PSI**I
      END DO

      FGAMMA=1.+(1.-CHI)*F1+CHI*F2
C
C     FINAL 
C
C      REDUCE GAMMA BY TRIAL AND ERROR FOR EXCL. VOLUME EFFECTS
C
C       WRITE(*,*)K,FGAMMA
       IF(I_EXVOL.EQ.1)FGAMMA=SCALE*(FGAMMA-1.)+1.
C
C     LARGE ARGUMENT EXPANSION
C
C
       IF(KK.EQ.0)THEN
         S_KP_EXV=F_IP*FGAMMA
         RETURN
       ELSE
         CONST=100.*(F_IP*FGAMMA-PI/(10.*L))
         S_KP_EXV=PI/(K_MEM*L)+CONST/(K_MEM*K_MEM)

         RETURN
        END IF
      END




	  FUNCTION FI(X)
      IF(X.GT.0.05)THEN
         FI=3.*(SIN(X)-X*COS(X))/X**3
         RETURN
      ELSE
         FI=1.-0.1*X*X
      RETURN
      END IF
      END
	  
	  
	  
	  
	  
	    FUNCTION S_EXV_APP(Q)
        X=Q**2
        IF(X.LT.0.01)THEN
          S_DEB=1.-0.333333333*X
        ELSE
          IF(X.GT. 74.)THEN
             AEXP=0.
           ELSE
             AEXP=EXP(-X)
           END IF
           S_DEB=2.*(AEXP+X-1.)/X**2
         END IF

         W=0.5*(TANH((Q-1.523)/0.1477)+1.)
         IF(Q.LT.0.3)THEN
           W=0.
           GOTO 10
         END IF

         Y2=1.220/Q**(1.709)+0.4288/Q**3.419
     $      -1.651/Q**5.128


10       S_EXV_APP=(1.-W)*S_DEB+W*Y2

         RETURN
         END
		
		
		

      FUNCTION SI(X)
C*************      IMPLICIT DOUBLE PRECISION (A-H, O-Z)
C
C     TEST ARGUMENT RANGE
C
      PI2=1.57079
      Z=ABS(X)
      IF(Z-4.) 10,10,50
C
C     Z IS NOT GREATER THAN 4
C
   10 Y=Z*Z
     0 SI=PI2+(-1.5707963+X*((((((.97942154E-11*Y-.22232633E-8)*Y
     X +.30561233E-6
     1 )*Y-.28341460E-4)*Y+.16666582E-2)*Y-.55555547E-1)*Y+1.))
C
C     TEST FOR LOGARITHMIC SINGULARITY
C
      IF(Z) 30,20,30
   20 CONTINUE
C**      CI=-1.70D38
      RETURN
   30 CONTINUE
C**     0CI=0.57721566+LOG(Z)-Y*(((((-.13869851E-9*Y+.26945842E-7)*Y-
C**     1.30952207E-5)*Y+.23146303E-3)*Y-.10416642E-1)*Y+.24999999)
   40 RETURN
C
C     Z IS GREATER THAN 4.
C
   50 SI=SIN(Z)
      Y=COS(Z)
      Z=4./Z
     0U=((((((((.40480690E-2*Z-.022791426)*Z+.055150700)*Z-.072616418)*Z
     1+.049877159)*Z-.33325186E-2)*Z-.023146168)*Z-.11349579E-4)*Z
     2+.062500111)*Z+.25839886E-9
     0V=(((((((((-.0051086993*Z+.028191786)*Z-.065372834)*Z+.079020335)*
     1Z-.044004155)*Z-.0079455563)*Z+.026012930)*Z-.37640003E-3)*Z
     2-.031224178)*Z-.66464406E-6)*Z+.25000000
C**      CI=Z*(SI*V-Y*U)
      SI=PI2-Z*(SI*U+Y*V)
C
C     TEST FOR NEGATIVE ARGUMENT
C
      IF(X) 60,40,40
C
C     X IS LESS THAN -4.
C
   60 SI=PI2+(-3.1415927-SI)
      RETURN
      END
	  