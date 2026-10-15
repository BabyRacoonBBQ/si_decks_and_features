
line x location= 0.0      spacing= 0.05<um> tag= subTop
line x location= 0.1<um>  spacing= 0.05<um> tag= subBottom
line y location=-0.1<um>  spacing= 0.05<um>
line y location= 0.05<um> spacing= 0.05<um>
line z location= 0.0<um>  spacing= 0.1<um>
line z location= 0.7<um>  spacing= 0.1<um>

region Silicon
init wafer.orient= { 0 0 1 } notch.direction= { 1 1 0 }

pdbSet Grid SnMesh min.normal.size  0.020 ;# 20nm
pdbSet Grid SnMesh max.lateral.size 0.100 ;# 100nm
pdbSet Grid SnMesh normal.growth.ratio.3d 2.0
refinebox clear
refinebox name= active min= { -0.65 -0.1 0.0 } max= { -0.1 0.05 0.7 } \
	xrefine= 100<nm> yrefine= 100<nm> zrefine= 100<nm>
refinebox name= metal materials= Copper \
	xrefine= 50<nm> yrefine= 50<nm> zrefine= 50<nm>
refinebox interface.materials= { Copper Nitride Oxide }

pdbSet Mechanics EtchDepoRelax 1
pdbSet Mechanics StressHistory 1

mask clear
mask name= metal_1 left= 0.0 right= 0.1 front= 0.0 back= 0.45
mask name= via_12 left= 0.025 right= 0.1 front= 0.3 back= 0.4
mask name= metal_2 left= 0.0 right= 0.1 front= 0.25 back= 0.7

deposit Oxide temperature= 250<C> thickness= 0.1 type= isotropic
deposit Oxide temperature= 250<C> thickness= 0.2 type= isotropic
deposit Photoresist thickness= 0.1 type= isotropic mask= metal_1
etch Oxide temperature= 25<C> thickness= 0.2 type= anisotropic
deposit Copper temperature= 250<C> coord= -0.3 type= fill
strip Photoresist

deposit Nitride temperature= 250<C> coord= -0.35 type= fill
deposit Oxide temperature= 250<C> thickness= 0.1 type= isotropic
deposit Photoresist thickness= 0.1 type= isotropic mask= via_12
etch Oxide temperature= 25<C> thickness= 0.11 type= anisotropic
etch Nitride temperature= 25<C> thickness= 0.1 type= anisotropic
deposit Copper temperature= 250<C> coord= -0.46 type= fill
strip Photoresist

deposit Oxide temperature= 250<C> coord= -0.65 type= fill
deposit Photoresist thickness= 0.1 type= isotropic mask= metal_2
etch Oxide temperature= 0<C> thickness= 0.2 type= anisotropic
deposit Copper temperature= 250<C> coord= -0.65 type= fill
strip Photoresist

deposit Nitride temperature= 250<C> coord= -0.7 type= fill

struct tdr=n1

