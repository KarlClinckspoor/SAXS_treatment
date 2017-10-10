<<<<<<< HEAD
import numpy as np
# This is a PEP8 mess, but it is like this to more easily correlate with the FORTRAN77 code.


def S_KP_EXV(Q, RL, RLL):
    # RL = contour_length
    # RRL = kuhn_length
    # I_EXVOL = 0:gaussian coils
    #            1: excluded volume effects included ----> this is set to 1 in the code,
    #               so I should ignore the rest where I_EXVOL = 0?
    # constant declarations
    # A1, A2, B1, B2, AA, BB: arrays
    # floats: K, L, K_MEM
    # assigns a ton of values to the arrays
    
    '''
    DIMENSION A1(2:5,0:2),A2(2:5,1:2),B1(0:2,0:2),B2(0:2,1:2)
    DIMENSION AA(2:5),BB(0:2)
    REAL K,L,K_MEM

    DATA A1,A2,B1,B2/
    -0.1222,0.3051,-0.0711,0.0584
    1.761,2.252,-1.291,0.6994,
    -26.04,20.00,4.382,1.594

    0.1212,-0.4169,0.1988, 0.3435,
    0.0170,-0.4731,0.1869,0.3350,

    -0.0699,-0.0900,0.2677,
     0.1342,0.0138,0.1898,
     -0.2020,-0.0114,0.0123,

     -0.5171,-0.2028,-0.3112,
     0.6950,-0.3238,-0.5403/

    '''
    # Matrices of excessive size, just so I don't have to deal with out of range indexes.
    A1 = np.zeros((6, 6))
    A2 = np.zeros((6, 6))
    B1 = np.zeros((6, 6))
    B2 = np.zeros((6, 6))
    AA = np.zeros(6)
    BB = np.zeros(6)
    
    A1[2, 0], A1[3, 0], A1[4, 0], A1[5, 0] = -0.1222, 0.3051, -0.0711, 0.0584
    A1[2, 1], A1[3, 1], A1[4, 1], A1[5, 1] = 1.761, 2.252, -1.291, 0.6994
    A1[2, 2], A1[3, 2], A1[4, 2], A1[5, 2] = -26.04, 20.00, 4.382, 1.594
    
    A2[2, 1], A2[3, 1], A2[4, 1], A2[5, 1] = 0.1212, -0.4169, 0.1988, 0.3435
    A2[2, 2], A2[3, 2], A2[4, 2], A2[5, 2] = 0.0170, -0.4731, 0.1869, 0.3350
    
    B1[0, 0], B1[1, 0], B1[2, 0] = -0.0699, -0.0900, 0.2677
    B1[0, 1], B1[1, 1], B1[2, 1] = 0.1342, 0.0138, 0.1898
    B1[0, 2], B1[1, 2], B1[2, 2] = -0.2020, -0.0114, 0.0123
    
    B2[0, 1], B2[1, 1], B2[2, 1] = -0.5171, -0.2028, -0.3112
    B2[0, 2], B2[1, 2], B2[2, 2] = 0.6950, -0.3238, -0.5403
    
    PI = np.pi
    K = Q * RLL
    L = RL/RLL
    I_EXVOL = 1
    SCALE = 1
    KK = 0
    
    if K > 10:
        K_MEM = K
        K = 10
        KK = 1
    
    # Rg**2 of debye function
    
    if I_EXVOL == 0:  # ignore, never is
        AEXP = 2 * L
        if AEXP > 74:
            AEXP = 0
        else:
            AEXP = np.exp(-AEXP)
        S2 = L/6 - 0.25 + 0.25/L - (1 - AEXP)/(8 * L * L)  # L * L == L**2 right?
        
        U = S2 * K * K
        AEXP = U
        
        if AEXP > 74:
            AEXP = 0
        else:
            AEXP = np.exp(-AEXP)
        
        if U < 0.01:
            F_DEBYE = 1 - 0.3333333*U
        else:
            F_DEBYE = 2 * (AEXP + U - 1) / U ** 2
    
    # Excluded volume effects
    
    else:  # if I_EXVOL == 1
        AEXP = 2 * L
        if AEXP > 60:
            AEXP = 0
        else:
            AEXP = np.exp(-AEXP)
        
        EPSI = 0.17
        EXPAN = (1 + (abs(L / 3.12) ** 2) + abs(L / 8.67) ** 3) ** (EPSI / 3)
        S2 = L / 6 - 0.25 + 0.25 / L - (1 - AEXP) / (8 * L * L)
        S2 = S2 * EXPAN

        # print('Debug: RG =', np.sqrt(S2))
        # print('Debug: EXP =', np.sqrt(EXPAN))

        F_DEBYE = S_EXV_APP(K * np.sqrt(S2))  # what is it for?
        # print('Debug:', F_DEBYE)
    
    # Rod scattering function
    
    A = K * L
    # F_ROD = 2 * SI(A) / A - (4 / (A ** 2)) * (np.sin(0.5 * A)) ** 2
    F_ROD = 2 * SI_weird(A) / A - (4 / (A ** 2)) * (np.sin(0.5 * A)) ** 2
    # the builtin function is not the same as the function used by the fortran code, for some reason. I rewrote it.
    
    # what is SI? Computes the sine and cosine integral. Also called the sine cardinal function.
    # numpy has it, it's np.sinc, but it's normalized by pi, so I need to divide by pi in order to remove that.
    # SI(X) = integral (sin(t)/t) summed over T from infinity to X
    
    # Weight CHI
    
    if I_EXVOL == 0:
        PSI = PI * S2 * K / (2 * L)
    else:
        PSI = K * ((PI / abs(1.103 * L)) ** 1.5) * (S2 ** 1.282)
    
    AEXP = 1 / (PSI ** 5)
    
    if AEXP > 74:
        CHI = 0
    else:
        CHI = np.exp(-AEXP)
    
    # interpolated function
    
    F_IP = (1 - CHI) * F_DEBYE + CHI * F_ROD
        
    # Correction Function FGAMMA
    # Calculate A'S
    
    AEXP = 40 / (4 * L)
    
    if AEXP > 74:
        AEXP = 0
    else:
        AEXP = np.exp(-AEXP)
    
    AEXP1 = 2 * L
    
    if AEXP1 > 74:
        AEXP = 0
    else:
        AEXP1 = np.exp(-AEXP1)

    # These two loops are correct, checked with the FORTRAN CODE
    for i in range(2, 5 + 1, 1):
        AA[i] = 0
        for ii in range(0, 2 + 1, 1):
            if ii == 0:
                AA[i] = AA[i] + A1[i, ii] / (L ** ii) * AEXP
                # print(i, ii, AA[i])
            else:
                AA[i] = AA[i] + A1[i, ii] / (L ** ii) * AEXP + A2[i, ii] * (L ** ii) * AEXP1
                # print(i, ii, AA[i])
    
    # Calculate B'S
    for i in range(0, 2 + 1, 1):
        BB[i] = 0
        for ii in range(0, 2 + 1, 1):
            if ii == 0:
                BB[i] = BB[i] + B1[i, ii] / (L ** ii)
                # print(i, ii, BB[i])
            else:
                BB[i] = BB[i] + B1[i, ii] / (L ** ii) + B2[i, ii] * L ** ii * AEXP1
                # print(i, ii, BB[i])
    
    # Calculate FGAMMA

    F1 = 0
    F2 = 0
    for i in range(2, 5 + 1, 1):
        F1 = F1 + AA[i] * PSI ** i
    for i in range(0, 2 + 1, 1):
        F2 = F2 + BB[i] / PSI ** i
    
    FGAMMA = 1 + (1 - CHI) * F1 + CHI * F2

    # Final Function
    # Reduce Gamma by trial and error for excluded volume effects

    if I_EXVOL == 1:
        FGAMMA = SCALE * (FGAMMA - 1) + 1
        
    # Large Argument Expansion
    
    if KK == 0:
        S_KP_EXV = F_IP * FGAMMA
        return S_KP_EXV
    else:
        CONST = 100 * (F_IP * FGAMMA - PI / (10 * L))
        S_KP_EXV = PI / (K_MEM * L) + CONST / (K_MEM * K_MEM)
        return S_KP_EXV


def S_EXV_APP(Q):
    X = Q ** 2
    if X < 0.01:
        S_DEB = 1 - 0.333333333 * X
    else:
        if X > 74:
            AEXP = 0
        else:
            AEXP = np.exp(-X)
        S_DEB = 2 * (AEXP + X - 1) / (X ** 2)
    
    W = 0.5 * (np.tanh((Q - 1.523) / 0.1477) + 1)
    if Q < 0.3:
        W = 0
        Y2 = 0
    else:
        Y2 = 1.220 / (Q ** 1.709) + 0.4288 / (Q ** 3.419) - 1.651 / (Q ** 5.128)

    S_EXV_APP = (1 - W * S_DEB + W * Y2)
    return S_EXV_APP


# For some reason, not really usable in this code. You have to use SI_weird to make it work.
def SI_new(x):
    return np.sinc(x/np.pi)


# The builtin SI function does not correlate with the SI function used in the FORTRAN code. I tested some values
# with the FORTRAN code, using gfortran to compile it, to check. Then, I translated the code into python, basically
# keeping everything the same -- the syntaxes are relatively compatible.
# Note: This should be because this SI function is integrated, while the np.sinc function is not. Trivial problem!
def SI_weird(X):
    PI2 = 1.57079
    Z = abs(X)
    if (Z-4) <= 0: # goto 10, 10
        Y = Z * Z
        SI = (PI2 + (-1.5707963 + X * ((((((.97942154E-11 * Y - .22232633E-8) * Y
        + .30561233E-6
         )*Y - .28341460E-4)*Y + .16666582E-2)*Y - .55555547E-1)*Y + 1.)))
        return SI

    if (Z-4) > 0:  # goto 50
        SI = np.sin(Z)
        Y = np.cos(Z)
        Z = 4. / Z
        U = ((((((((.40480690E-2 * Z - .022791426) * Z + .055150700) * Z - .072616418) * Z
             + .049877159) * Z - .33325186E-2) * Z - .023146168) * Z - .11349579E-4) * Z
         + .062500111) * Z + .25839886E-9
        V = (((((((((-.0051086993 * Z + .028191786) * Z - .065372834) * Z + .079020335) *
              Z - .044004155) * Z - .0079455563) * Z + .026012930) * Z - .37640003E-3) * Z
          - .031224178) * Z - .66464406E-6) * Z + .25000000
        SI = PI2 - Z * (SI * U + Y * V)
        return SI

    #if X < 0:
    #    SI = PI2 + (-3.1415927 - SI)
    #    return SI
    #if X >= 0:


# Code
# Function S_KP_EXV:
"""
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
C     R_G^2 OF DEBYE FUNCTION
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
C     DEBYE FUNCTION
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
C     ROD SCATTERING FUNCTION
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
C     INTERPOLATED FUNCTION
C

        F_IP=(1.-CHI)*F_DEBYE+CHI*F_ROD
C
C     CORRECTION FUNCTION FGAMMA
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
             AA(I)=AA(I)+A1(I,II)/L**II*AEXP
           ELSE
             AA(I)=AA(I)+A1(I,II)/L**II*AEXP+A2(I,II)*L**II*AEXP1
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
C     FINAL FUNCTION
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

"""

# Function S_EXV_APP:
"""
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
"""

# Function SI:
"""

C
CC
C     ..................................................................
C
C        FUNCTION SI(X)
C
C        PURPOSE
C           COMPUTES THE SINE AND COSINE INTEGRAL
C
C
C        DESCRIPTION OF PARAMETERS
C           SI    - THE RESULTANT VALUE SI(X)
C           X     - THE ARGUMENT OF SI(X)
C
C        REMARKS
C           THE ARGUMENT VALUE REMAINS UNCHANGED
C
C        SUBROUTINES AND FUNCTION SUBPROGRAMS REQUIRED
C           NONE
C
C        METHOD
C           DEFINITION
C           SI(X)=INTEGRAL(SIN(T)/T, SUMMED OVER T FROM INFINITY TO X)
C           EVALUATION
C           REDUCTION OF RANGE USING SYMMETRY.
C           DIFFERENT APPROXIMATIONS ARE USED FOR ABS(X) GREATER
C           THAN 4 AND FOR ABS(X) LESS THAN 4.
C           REFERENCE
C           LUKE AND WIMP, 'POLYNOMIAL APPROXIMATIONS TO INTEGRAL
C           TRANSFORMS',  MATHEMATICAL TABLES AND OTHER AIDS TO
C           COMPUTATION, VOL. 15, 1961, ISSUE 74, PP. 174-178.
C
C     ..................................................................
C
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
"""
=======
import numpy as np
# This is a PEP8 mess, but it is like this to more easily correlate with the FORTRAN77 code.


def S_KP_EXV(Q, RL, RLL):
    # RL = contour_length
    # RRL = kuhn_length
    # I_EXVOL = 0:gaussian coils
    #            1: excluded volume effects included ----> this is set to 1 in the code,
    #               so I should ignore the rest where I_EXVOL = 0?
    # constant declarations
    # A1, A2, B1, B2, AA, BB: arrays
    # floats: K, L, K_MEM
    # assigns a ton of values to the arrays
    
    '''
    DIMENSION A1(2:5,0:2),A2(2:5,1:2),B1(0:2,0:2),B2(0:2,1:2)
    DIMENSION AA(2:5),BB(0:2)
    REAL K,L,K_MEM

    DATA A1,A2,B1,B2/
    -0.1222,0.3051,-0.0711,0.0584
    1.761,2.252,-1.291,0.6994,
    -26.04,20.00,4.382,1.594

    0.1212,-0.4169,0.1988, 0.3435,
    0.0170,-0.4731,0.1869,0.3350,

    -0.0699,-0.0900,0.2677,
     0.1342,0.0138,0.1898,
     -0.2020,-0.0114,0.0123,

     -0.5171,-0.2028,-0.3112,
     0.6950,-0.3238,-0.5403/

    '''
    # Matrices of excessive size, just so I don't have to deal with out of range indexes.
    A1 = np.zeros((6, 6))
    A2 = np.zeros((6, 6))
    B1 = np.zeros((6, 6))
    B2 = np.zeros((6, 6))
    AA = np.zeros(6)
    BB = np.zeros(6)
    
    A1[2, 0], A1[3, 0], A1[4, 0], A1[5, 0] = -0.1222, 0.3051, -0.0711, 0.0584
    A1[2, 1], A1[3, 1], A1[4, 1], A1[5, 1] = 1.761, 2.252, -1.291, 0.6994
    A1[2, 2], A1[3, 2], A1[4, 2], A1[5, 2] = -26.04, 20.00, 4.382, 1.594
    
    A2[2, 1], A2[3, 1], A2[4, 1], A2[5, 1] = 0.1212, -0.4169, 0.1988, 0.3435
    A2[2, 2], A2[3, 2], A2[4, 2], A2[5, 2] = 0.0170, -0.4731, 0.1869, 0.3350
    
    B1[0, 0], B1[1, 0], B1[2, 0] = -0.0699, -0.0900, 0.2677
    B1[0, 1], B1[1, 1], B1[2, 1] = 0.1342, 0.0138, 0.1898
    B1[0, 2], B1[1, 2], B1[2, 2] = -0.2020, -0.0114, 0.0123
    
    B2[0, 1], B2[1, 1], B2[2, 1] = -0.5171, -0.2028, -0.3112
    B2[0, 2], B2[1, 2], B2[2, 2] = 0.6950, -0.3238, -0.5403
    
    PI = np.pi
    K = Q * RLL
    L = RL/RLL
    I_EXVOL = 1
    SCALE = 1
    KK = 0
    
    if K > 10:
        K_MEM = K
        K = 10
        KK = 1
    
    # Rg**2 of debye function
    
    if I_EXVOL == 0:  # ignore, never is
        AEXP = 2 * L
        if AEXP > 74:
            AEXP = 0
        else:
            AEXP = np.exp(-AEXP)
        S2 = L/6 - 0.25 + 0.25/L - (1 - AEXP)/(8 * L * L)  # L * L == L**2 right?
        
        U = S2 * K * K
        AEXP = U
        
        if AEXP > 74:
            AEXP = 0
        else:
            AEXP = np.exp(-AEXP)
        
        if U < 0.01:
            F_DEBYE = 1 - 0.3333333*U
        else:
            F_DEBYE = 2 * (AEXP + U - 1) / U ** 2
    
    # Excluded volume effects
    
    else:  # if I_EXVOL == 1
        AEXP = 2 * L
        if AEXP > 60:
            AEXP = 0
        else:
            AEXP = np.exp(-AEXP)
        
        EPSI = 0.17
        EXPAN = (1 + (abs(L / 3.12) ** 2) + abs(L / 8.67) ** 3) ** (EPSI / 3)
        S2 = L / 6 - 0.25 + 0.25 / L - (1 - AEXP) / (8 * L * L)
        S2 = S2 * EXPAN

        # print('Debug: RG =', np.sqrt(S2))
        # print('Debug: EXP =', np.sqrt(EXPAN))

        F_DEBYE = S_EXV_APP(K * np.sqrt(S2))  # what is it for?
        # print('Debug:', F_DEBYE)
    
    # Rod scattering function
    
    A = K * L
    # F_ROD = 2 * SI(A) / A - (4 / (A ** 2)) * (np.sin(0.5 * A)) ** 2
    F_ROD = 2 * SI_weird(A) / A - (4 / (A ** 2)) * (np.sin(0.5 * A)) ** 2
    # the builtin function is not the same as the function used by the fortran code, for some reason. I rewrote it.
    
    # what is SI? Computes the sine and cosine integral. Also called the sine cardinal function.
    # numpy has it, it's np.sinc, but it's normalized by pi, so I need to divide by pi in order to remove that.
    # SI(X) = integral (sin(t)/t) summed over T from infinity to X
    
    # Weight CHI
    
    if I_EXVOL == 0:
        PSI = PI * S2 * K / (2 * L)
    else:
        PSI = K * ((PI / abs(1.103 * L)) ** 1.5) * (S2 ** 1.282)
    
    AEXP = 1 / (PSI ** 5)
    
    if AEXP > 74:
        CHI = 0
    else:
        CHI = np.exp(-AEXP)
    
    # interpolated function
    
    F_IP = (1 - CHI) * F_DEBYE + CHI * F_ROD
        
    # Correction Function FGAMMA
    # Calculate A'S
    
    AEXP = 40 / (4 * L)
    
    if AEXP > 74:
        AEXP = 0
    else:
        AEXP = np.exp(-AEXP)
    
    AEXP1 = 2 * L
    
    if AEXP1 > 74:
        AEXP = 0
    else:
        AEXP1 = np.exp(-AEXP1)

    # These two loops are correct, checked with the FORTRAN CODE
    for i in range(2, 5 + 1, 1):
        AA[i] = 0
        for ii in range(0, 2 + 1, 1):
            if ii == 0:
                AA[i] = AA[i] + A1[i, ii] / (L ** ii) * AEXP
                # print(i, ii, AA[i])
            else:
                AA[i] = AA[i] + A1[i, ii] / (L ** ii) * AEXP + A2[i, ii] * (L ** ii) * AEXP1
                # print(i, ii, AA[i])
    
    # Calculate B'S
    for i in range(0, 2 + 1, 1):
        BB[i] = 0
        for ii in range(0, 2 + 1, 1):
            if ii == 0:
                BB[i] = BB[i] + B1[i, ii] / (L ** ii)
                # print(i, ii, BB[i])
            else:
                BB[i] = BB[i] + B1[i, ii] / (L ** ii) + B2[i, ii] * L ** ii * AEXP1
                # print(i, ii, BB[i])
    
    # Calculate FGAMMA

    F1 = 0
    F2 = 0
    for i in range(2, 5 + 1, 1):
        F1 = F1 + AA[i] * PSI ** i
    for i in range(0, 2 + 1, 1):
        F2 = F2 + BB[i] / PSI ** i
    
    FGAMMA = 1 + (1 - CHI) * F1 + CHI * F2

    # Final Function
    # Reduce Gamma by trial and error for excluded volume effects

    if I_EXVOL == 1:
        FGAMMA = SCALE * (FGAMMA - 1) + 1
        
    # Large Argument Expansion
    
    if KK == 0:
        S_KP_EXV = F_IP * FGAMMA
        return S_KP_EXV
    else:
        CONST = 100 * (F_IP * FGAMMA - PI / (10 * L))
        S_KP_EXV = PI / (K_MEM * L) + CONST / (K_MEM * K_MEM)
        return S_KP_EXV


def S_EXV_APP(Q):
    X = Q ** 2
    if X < 0.01:
        S_DEB = 1 - 0.333333333 * X
    else:
        if X > 74:
            AEXP = 0
        else:
            AEXP = np.exp(-X)
        S_DEB = 2 * (AEXP + X - 1) / (X ** 2)
    
    W = 0.5 * (np.tanh((Q - 1.523) / 0.1477) + 1)
    if Q < 0.3:
        W = 0
        Y2 = 0
    else:
        Y2 = 1.220 / (Q ** 1.709) + 0.4288 / (Q ** 3.419) - 1.651 / (Q ** 5.128)

    S_EXV_APP = (1 - W * S_DEB + W * Y2)
    return S_EXV_APP


# For some reason, not really usable in this code. You have to use SI_weird to make it work.
def SI_new(x):
    return np.sinc(x/np.pi)


# The builtin SI function does not correlate with the SI function used in the FORTRAN code. I tested some values
# with the FORTRAN code, using gfortran to compile it, to check. Then, I translated the code into python, basically
# keeping everything the same -- the syntaxes are relatively compatible.
# Note: This should be because this SI function is integrated, while the np.sinc function is not. Trivial problem!
def SI_weird(X):
    PI2 = 1.57079
    Z = abs(X)
    if (Z-4) <= 0: # goto 10, 10
        Y = Z * Z
        SI = (PI2 + (-1.5707963 + X * ((((((.97942154E-11 * Y - .22232633E-8) * Y
        + .30561233E-6
         )*Y - .28341460E-4)*Y + .16666582E-2)*Y - .55555547E-1)*Y + 1.)))
        return SI

    if (Z-4) > 0:  # goto 50
        SI = np.sin(Z)
        Y = np.cos(Z)
        Z = 4. / Z
        U = ((((((((.40480690E-2 * Z - .022791426) * Z + .055150700) * Z - .072616418) * Z
             + .049877159) * Z - .33325186E-2) * Z - .023146168) * Z - .11349579E-4) * Z
         + .062500111) * Z + .25839886E-9
        V = (((((((((-.0051086993 * Z + .028191786) * Z - .065372834) * Z + .079020335) *
              Z - .044004155) * Z - .0079455563) * Z + .026012930) * Z - .37640003E-3) * Z
          - .031224178) * Z - .66464406E-6) * Z + .25000000
        SI = PI2 - Z * (SI * U + Y * V)
        return SI

    #if X < 0:
    #    SI = PI2 + (-3.1415927 - SI)
    #    return SI
    #if X >= 0:


# Code
# Function S_KP_EXV:
"""
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
C     R_G^2 OF DEBYE FUNCTION
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
C     DEBYE FUNCTION
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
C     ROD SCATTERING FUNCTION
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
C     INTERPOLATED FUNCTION
C

        F_IP=(1.-CHI)*F_DEBYE+CHI*F_ROD
C
C     CORRECTION FUNCTION FGAMMA
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
             AA(I)=AA(I)+A1(I,II)/L**II*AEXP
           ELSE
             AA(I)=AA(I)+A1(I,II)/L**II*AEXP+A2(I,II)*L**II*AEXP1
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
C     FINAL FUNCTION
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

"""

# Function S_EXV_APP:
"""
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
"""

# Function SI:
"""

C
CC
C     ..................................................................
C
C        FUNCTION SI(X)
C
C        PURPOSE
C           COMPUTES THE SINE AND COSINE INTEGRAL
C
C
C        DESCRIPTION OF PARAMETERS
C           SI    - THE RESULTANT VALUE SI(X)
C           X     - THE ARGUMENT OF SI(X)
C
C        REMARKS
C           THE ARGUMENT VALUE REMAINS UNCHANGED
C
C        SUBROUTINES AND FUNCTION SUBPROGRAMS REQUIRED
C           NONE
C
C        METHOD
C           DEFINITION
C           SI(X)=INTEGRAL(SIN(T)/T, SUMMED OVER T FROM INFINITY TO X)
C           EVALUATION
C           REDUCTION OF RANGE USING SYMMETRY.
C           DIFFERENT APPROXIMATIONS ARE USED FOR ABS(X) GREATER
C           THAN 4 AND FOR ABS(X) LESS THAN 4.
C           REFERENCE
C           LUKE AND WIMP, 'POLYNOMIAL APPROXIMATIONS TO INTEGRAL
C           TRANSFORMS',  MATHEMATICAL TABLES AND OTHER AIDS TO
C           COMPUTATION, VOL. 15, 1961, ISSUE 74, PP. 174-178.
C
C     ..................................................................
C
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
"""
>>>>>>> c44b638e9b1b456f6420b32a842690de5490f94a
