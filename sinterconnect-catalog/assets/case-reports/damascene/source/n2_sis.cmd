init tdr=n1
mode mechanics
solve temperature= 25

SetPlxList { StressEL_xx StressEL_yy StressEL_zz }
WritePlx n2_via.plx y= 0.04 z= 0.35 Copper

struct tdr=n2

