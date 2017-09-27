C	  Compiled using gfortran.
      PROGRAM test
      DIMENSION A1(2:5,0:2),A2(2:5,1:2),B1(0:2,0:2),B2(0:2,1:2)
      DIMENSION AA(2:5),BB(0:2)
      REAL K,L,K_MEM,AEXP,AEXP1
      DATA A1,A2,B1,B2/-0.1222,0.3051,-0.0711,0.0584,1.761,2.252,
     $ -1.291,0.6994,-26.04,20.00,4.382,1.594,0.1212,-0.4169,0.1988,
     $ 0.3435,0.0170,-0.4731,0.1869,0.3350,-0.0699,-0.0900,0.2677,
     $ 0.1342,0.0138,0.1898,-0.2020,-0.0114,0.0123,-0.5171,-0.2028,
     $ -0.3112,0.6950,-0.3238,-0.5403/
	  
	  K = 1
	  L = 1
	  K_MEM = 1
	  AEXP = 1
	  AEXP1 = 1
	  
	  WRITE(*,*) 'CALCULATE AS'
      DO I=2,5
        AA(I)=0.
          DO II=0,2
           IF(II.EQ.0)THEN
             AA(I)=AA(I)+A1(I,II)/L**II*AEXP
			 WRITE(*,*)I,II,AA(I)
           ELSE
             AA(I)=AA(I)+A1(I,II)/L**II*AEXP+A2(I,II)*L**II*AEXP1
			 WRITE(*,*)I,II,AA(I)
           END IF
         END DO
      END DO
C
C     CALULATE B'S
C
	  WRITE(*,*) 'CALCULATE BS'
	  DO I=0,2
        BB(I)=0.
          DO II=0,2
           IF(II.EQ.0)THEN
             BB(I)=BB(I)+B1(I,II)/L**II
			 WRITE(*,*)I,II,BB(I)
           ELSE
             BB(I)=BB(I)+B1(I,II)/L**II+B2(I,II)*L**II*AEXP1
			 WRITE(*,*)I,II,BB(I)
           END IF
         END DO
      END DO
	 
	  END PROGRAM