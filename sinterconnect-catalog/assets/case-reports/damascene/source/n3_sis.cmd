init tdr=n2

contact Copper name= upper box sidewall \
	xlo= -0.65 xhi= -0.45 ylo= 0.0 yhi= 0.05 zlo= 0.7 zhi= 0.7
contact Copper name= lower box sidewall \
	xlo= -0.30 xhi= -0.10 ylo= 0.0 yhi= 0.05 zlo= 0.0 zhi= 0.0
contact Silicon name= tm0 box  \
	xlo= 0.0 xhi= 0.0 ylo= -0.1 yhi= 0.05 zlo= 0.0 zhi= 0.7
contact Nitride name= tm1 box  \
	xlo= -0.7 xhi= -0.7 ylo= -0.1 yhi= 0.05 zlo= 0.0 zhi= 0.7

supply contact.name= upper voltage= 0.1<V>
supply contact.name= lower voltage= 0.0<V>
supply contact.name= tm0 temperature= 100<C>
supply contact.name= tm1 temperature= 25<C>

mode mechanics current thermal
solve time= 1<s>
struct tdr= n3



