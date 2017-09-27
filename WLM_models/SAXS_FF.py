# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 13:17:45 2017

@author: Karl
"""

import numpy as np
from numpy import sin, cos
import matplotlib.pyplot as plt
from scipy.special import jv
from scipy import integrate
from S_KP_EXV import *
# Not really a problem since S_KP_EXV has only a few functions, and no overlap.


def sphere_FF(q, R):
    if R == 0:
        return 0
    FF = ((3 * (sin(q * R) - q * R * cos(q * R)) / (q * R) ** 3) ** 2)
    return FF


def FI(X):
    if X > 0.05:
        FI = 3 * (sin(X) - X * cos(X))/(X**3)
        return FI
    else:
        FI = 1 - 0.1 * X * X
        return FI


def spherical_shell(q, R1, R2):
    def V(R):
        return 4 / 3 * np.pi * R ** 3

    if R1 < R2:
        return (V(R2) * sphere_FF(q, R2) - V(R1) * sphere_FF(q, R1)) / (V(R2) - V(R1))
    if R1 > R2:
        return (V(R1) * sphere_FF(q, R1) - V(R2) * sphere_FF(q, R2)) / (V(R1) - V(R2))


def Bessel():
    orders = [0, 1, 2, 3, 4, 5]
    x = np.linspace(0, 10, 500)
    for order in orders:
        plt.plot(x, jv(order, x))

    plt.show()


def Cylinder_FF_to_integrate3(q, R, L, al):
    qrsin = q*R*sin(al)
    qlcos = q*L*cos(al)/2
    
    value = (2*jv(1, qrsin)/qrsin * sin(qlcos)/qlcos)**2 * sin(al)
    return value


# Common units: R = 30, L = 120, length = 500, qs = np.logspace(-2, 0, num = length)
def Cylinder_FF_integrated(qs, R, L):
    """Uses simpson integration method to get the form function of a cylinder with the dimensions L and R"""
    alphas = np.linspace(1e-2, np.pi / 2, num=50)
    int_simps = np.zeros(len(qs))
    to_int_simps = np.zeros(len(qs))

    for i, q in enumerate(qs):
        for j, alpha in enumerate(alphas):
            qrsin = q * R * sin(alpha)
            qlcos = q * L * cos(alpha) / 2
            to_int_simps[j] = (2 * jv(1, qrsin) / qrsin * sin(qlcos) / qlcos) ** 2 * sin(alpha)
        int_simps[i] = integrate.simps(to_int_simps, x=alphas)

    return int_simps


def Guinier(I0, q, Rg):
    return I0*np.exp(-(q**2*Rg**2)/3)


def Ellipsoid_to_int(q, R, Ep, Th):
    def r_f(R, Ep, Th):
        return R * (sin(Th) ** 2 + Ep ** 2 * cos(Th) ** 2) ** (1 / 2)
    r = r_f(R, Ep, Th)
    Num = 3 * (sin(q*r) - q*r*cos(q*r))
    Den = (q*r)**3
    to_int = (Num/Den)**2*sin(Th)
    return to_int


# todo
def Ellipsoid_integrated(q, R, Ep, Th):
    def r_f(R, Ep, Th):
        return R * (sin(Th) ** 2 + Ep ** 2 * cos(Th) ** 2) ** (1 / 2)



def wormlike_chains(q, scale, d_head, Rcore, rho_rel, sigma, back, cont_l, kuhn_l, eps, dist_cq, nu_ppa,
                    scale_pow, exponent):
    Rout = Rcore + d_head
    FX = (((rho_rel * Rout ** 2 * 2 * jv(1, Rout * q) / (q * Rout)) -
           ((rho_rel + 1) * Rcore ** 2 * 2 * jv(1, Rcore * q) / (q * Rcore))) *
          np.exp((-1/2) * q ** 2 * sigma ** 2))

    FOX = rho_rel * Rout ** 2 - (rho_rel + 1) * Rcore ** 2

    cyl_int = 0  # SUM
    npoints = 50
    step = 0.5 * np.pi / npoints

    EPSO = (Rcore * eps + d_head) / Rout
    for i in range(1, npoints + 1):
        alpha = (i - 0.5) * step
        sinalpha = sin(alpha)

        SC = np.sqrt(sinalpha ** 2 + eps ** 2 * (1 - sinalpha ** 2))
        RA = Rcore * SC

        # RO = R + A(2)  - unnecessary
        SCO = np.sqrt(sinalpha ** 2 + EPSO ** 2 * (1 - sinalpha ** 2))
        RAO = Rout * SCO

        F = (((EPSO * rho_rel * Rout ** 2 * 2 * jv(1, RAO * q) / (q * RAO)) -
              ((rho_rel + 1) * eps * Rcore ** 2 * 2 * jv(1, RA * q) / (q * RA))) *
             np.exp((-0.5) * q ** 2 * sigma ** 2))
        cyl_int = cyl_int + F ** 2  # === SUM=SUM+F**2

    cyl_int = cyl_int * step * 2 / np.pi
    FO = EPSO * rho_rel * Rout ** 2 - (rho_rel + 1) * eps * Rcore ** 2
    # if J == 1:
    # print (qs, FX ** 2, FOX ** 2, cyl_int, FO ** 2)
    SQ = S_KP_EXV(q, cont_l, kuhn_l)

    CQ = FI(q * dist_cq)
    FORMF = SQ * cyl_int / (FO ** 2)
    Rout = abs(d_head) + abs(Rcore)  # necessary?

    FORMFX = SQ  # 2 * jv(1, qs * Rout) / (qs * Rout) ** 2

    XSEC = scale * FORMF / (1 + nu_ppa * CQ * FORMFX) + back + scale_pow* (0.01 / q) ** exponent

    return XSEC

def WLM_whole_q(qs, scale, d_head, rad_core, rho_rel, sigma, back, L, kuhn, eps, D_CQ, nu_rpa, SC_pow, exponent):
    ints = np.zeros(len(qs))
    for i, q in enumerate(qs):
        ints[i] = wormlike_chains(q, scale, d_head, rad_core, rho_rel, sigma, back, L, kuhn, eps, D_CQ, nu_rpa,
                                  SC_pow, exponent)
    return ints

def coreshell_micelles(q, scale, d_head, a, b, c, rho_out, sigma, back, eta_hs, r_hs):
    
#       A(1) = SCALE
#       A(2) = D_HEAD
#       A(3) = A-AXE
#       A(4) = B-AXE
#       A(5) = C-AXE
#       A(6) = RHO_OUT
#       A(7) = SIGMA
#       A(8) = BACKGROUND
#       A(9) = ETA_HS
#       A(10) = R_HS
    
    PI = np.pi()
    
    NPOI = 50
    STEP = 0.5 * PI / NPOI
    
    SUM = 0
    SUM1 = 0

    # Graded interface factor
    
    GRAD_O = np.exp(-q * q * sigma * sigma * 0.5)
    GRAD_I = np.exp(-q * q * sigma * sigma * 0.5)
    
    DRHO_CORE = -1
    V_CORE = 4 * PI / 3 * a * b * c
    V_OUT = 3 * PI / 3 * (a + d_head) * (b + d_head) * (c + d_head)
    V_SHELL = V_OUT - V_CORE
    DRHO_HEAD = rho_out
    
    for III in range (1, NPOI + 1, 1):
        YY = (float(III) - 0.5) * STEP
        YY = sin(YY)
        for II in range (1, NPOI + 1, 1):
            XX = (float(II) - 0.5) * STEP
            XX = sin(XX)
            
            ARG_C = np.sqrt((a ** 2 * YY ** 2 + b ** 2 * (1-YY ** 2)) * XX** 2 + c ** 2 * (1 - XX ** 2))
            
            ARG_O = np.sqrt(((a+d_head) ** 2 * YY ** 2 + (b + d_head) ** 2 * (1 - YY ** 2)) * XX ** 2 + (c + d_head) ** 2 * (1 - XX ** 2))
            
            FF = V_OUT * DRHO_HEAD * FI(q * ARG_O) * GRAD_O - V_CORE * (DRHO_HEAD - DRHO_CORE) * FI(q * ARG_C) * GRAD_I
            
            SUM = SUM + FF ** 2 ** XX
            SUM1 = SUM1 + FF * XX
    
    F0 = V_OUT * DRHO_HEAD - V_CORE * (DRHO_HEAD - DRHO_CORE)
    
    F2 = SUM * STEP ** 2 / F0 ** 2 * 2 * PI
    FFF = SUM1 * STEP ** 2 / F0 * 2 / PI
    
    #print(q, F2, FFF, FFF ** 2)
    
    SQ = S_HS(q, r_hs, eta_hs)
    XSEC = scale * (F2 + FFF ** 2 * (SQ - 1)) + back
    
    return XSEC

def S_HS(Q, RHS, ETA):
    # Hard sphere structure factor
    # q = scattering vector
    # r_hs = interaction radius of hard spheres
    # eta = volume fraction of hard spheres
    
    ALN = (1 - ETA) ** 4
    AL = (1 + 2 * ETA) ** 2 / ALN
    BE = -6 * ETA * (1 + 0.5 * ETA) ** 2 / ALN
    GA = 0.5 * ETA * AL
    AR = 0.5 * ETA * AL
    
    # Low argument expansion
    
    if AR < 0.4:
        GG = (AL * (1/3 - AR * AR / 30) + BE * (1/4 - AR * AR / 36)
              # + GA * (1/6 - AR * AR / 48)
              # Check if ! at the 6th position is comment or a code to continue the line.
              )
    else:
        SA = sin(AR)
        CA = cos(AR)
        GG = (AL * (SA - AR * CA) / AR **3
              # + BE * (2 * AR * SA + (2 - AR ** 2) * CA - 2) / AR ** 4 + GA *
              # (-AR ** 4 * CA + 4 * ((3 * AR ** 2 - 6) * CA + (AR ** 3 - 6 * AR) * SA + 6)) / AR ** 6
              )
    S_HS = 1 / (1 + 24 * ETA * GG)
    return S_HS
    
if __name__ == '__main__':
    q = 1
    r_hs = 1
    eta = 0.01

    print(q, r_hs, eta, S_HS(q, r_hs, eta))
    """
    npoints = 50
    # qs = np.logspace(np.log10(5.11423033E-03), np.log10(0.254317015), num = npoints)
    qs = np.logspace(-2.29, -0.59, num=npoints)

    scale = 0.1440E+00
    d_head = 0.1929E+02
    rad_core = 0.8109E+01
    rho_rel = 0.5999E-01
    sigma = 0.1000E+01
    back = 0.0
    L = 0.5000E+04
    kuhn = 0.1000E+04
    eps = 0.1000E+01
    D_CQ = 0.1050E+03
    nu_rpa = 0.3846E+02
    SC_pow = 0.6757E-03
    exponent = 4

    # parameters = [scale, d_head, rad_core, rho_rel, sigma, back, L, kuhn, eps, D_CQ, nu_rpa, SC_pow, exponent]
    # parameters = np.array(parameters)

    nus = [20, 30, 40, 50, 60, 70, 80]
    D_CQs = [40, 80, 100, 120, 150, 200]

    ints_nu = []
    for nu in nus:
        scatt = WLM_whole_q(qs, scale, d_head, rad_core, rho_rel, sigma, back, L, kuhn, eps, D_CQ, nu,
                                  SC_pow, exponent)
        ints_nu.append(scatt)

    ints_cqs = []
    for cq in D_CQs:
        scatt = WLM_whole_q(qs, scale, d_head, rad_core, rho_rel, sigma, back, L, kuhn, eps, cq, nu_rpa,
                                  SC_pow, exponent)
        ints_cqs.append(scatt)

    plt.xscale('log')
    plt.yscale('log')
    for int, nu in zip(ints_nu, nus):
        plt.plot(qs, int, label = ('Nu = ' + str(nu)))
    plt.legend()
    plt.show()

    plt.xscale('log')
    plt.yscale('log')
    for int, cq in zip(ints_cqs, D_CQs):
        plt.plot(qs, int, label = ('CQ = ' + str(cq)))
    plt.legend()
    plt.show()

    # for i, q in enumerate(qs):
    #    ints[i] = wormlike_chains(q, scale, d_head, rad_core, rho_rel, sigma, back, L, kuhn, eps, D_CQ, nu_rpa,
    #                              SC_pow, exponent)
    
    """

    """
    with open('SAXS_test.dat', 'r') as fhand:
        q_test = []
        int_test = []
        for line in fhand:
            line = line.strip()
            line = line.split(' ')
            if len(line) < 3:
                continue
            q, Int, err = line
            q_test.append(float(q)/10)
            int_test.append(float(Int))
    
    plt.xscale('log')
    plt.yscale('log')
    plt.plot(qs, ints)
    plt.plot(q_test, int_test)
    plt.title('Sim1')
    plt.savefig('sucesso.png')
    plt.show()
    """
# FORTRAN 77 Source code
# Function FI
"""
      FUNCTION FI(X)
      IF(X.GT.0.05)THEN
         FI=3.*(SIN(X)-X*COS(X))/X**3
         RETURN
      ELSE
         FI=1.-0.1*X*X
      RETURN
      END IF
      END
"""

# Function wormlike micellar core-shell chain
"""
       IF(NXS.EQ.2)THEN

c      infinite core-shell cylinders
C
C      A(1) = SCALE
C      A(2) = D_HEAD
C      A(3) = R_IN
C      A(4) = REL_RHO_OI
C      A(5) = SIGMA
C      A(6) = BACKGROUND
C      A(7) = CONTOUR LENGTH
C      A(8) = KUHN LENGTH
C      A(9) = EPS XSEC

        RO=A(3)+A(2)
        R=A(3)
        EPS=A(9)
        BCK=A(6)
C
        PI=ACOS(-1.)

        FX=( A(4)*RO**2* 2.*BESSJ1(RO*X(1))/(X(1)*RO)
     1  -(A(4)+1.)*A(3)**2*2.*BESSJ1(A(3)*X(1))/(X(1)*A(3))
     1  )  *EXP(-0.5*X(1)**2*A(5)**2)

        F0X=A(4)*RO**2-(A(4)+1.)*A(3)**2

        SUM=0.
        NPOI=50
        STEP=0.5*ACOS(-1.)*1./FLOAT(NPOI)

       DO II=1,NPOI
          XX=(FLOAT(II)-0.5)*STEP
          XX=SIN(XX)
          SC=SQRT(XX**2+EPS**2*(1.-XX**2))
          RA=R*SC

          RO=R+A(2)
          EPSO=(R*EPS+A(2))/RO
          SCO=SQRT(XX**2+EPSO**2*(1.-XX**2))
          RAO=RO*SCO


        F=( EPSO*A(4)*RO**2* 2.*BESSJ1(RAO*X(1))/(X(1)*RAO)
     1  -(A(4)+1.)*EPS*A(3)**2*2.*BESSJ1(RA*X(1))/(X(1)*RA)
     1  )  *EXP(-0.5*X(1)**2*A(5)**2)

        SUM=SUM+F**2

        END DO

        SUM=SUM*STEP*2./PI

        F0=EPSO*A(4)*RO**2-(A(4)+1.)*EPS*A(3)**2

        IF(J.EQ.1)WRITE(*,*)X(1),FX**2,F0X**2,SUM,F0**2

        SQ=S_KP_EXV(X(1),A(7),A(8))
C
C      PRISM-RPA CONCENTRATION EFFECTS
C
       CQ=FI(X(1)*A(10))
C
       FORMF=SQ*SUM/(F0)**2
       RO=ABS(A(2))+ABS(A(3))
c       FORMFX=SQ*(2.*BESSJ1(X(1)*RO)/(X(1)*RO))**2
       FORMFX=SQ

       XSEC=A(1)*FORMF/(1.+A(11)*CQ*FORMFX)+BCK
     1    +A(12)*(0.01/X(1))**A(13)
       RETURN
       END IF
"""
