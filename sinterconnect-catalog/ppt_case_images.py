"""Case-image associations reviewed against StressThermal.pptx slide context.

Images are extracted unchanged. Mechanics overview illustrations are explicitly
distinguished from simulation results for a particular archived input deck.
"""
CASE_IMAGES = {
    'Package_Reliability': ('Simulation contours', [
        ('slide-4-image-2.gif', 'Temperature'),
        ('slide-4-image-3.gif', 'Equivalent stress'),
    ]),
    'Submodeling': ('Simulation contours', [
        ('slide-5-image-2.png', 'Global pillar array — equivalent stress'),
        ('slide-5-image-3.png', 'Single-pillar submodel — equivalent stress'),
        ('slide-7-image-1.png', 'Global equivalent stress — scale capped at 600 MPa'),
        ('slide-7-image-2.png', 'Local equivalent stress — scale capped at 600 MPa'),
    ]),
    'Quasistatic': ('Mechanics illustration', [
        ('slide-2-image-1.gif', 'Quasistatic stress distribution'),
    ]),
    'Linear_Buckling': ('Mechanics illustration', [
        ('slide-2-image-3.png', 'Buckling modes 1, 2 and 3'),
    ]),
    'Post_Buckling': ('Mechanics illustration', [
        ('slide-2-image-4.gif', 'Snap-through behavior'),
    ]),
    'Large_Deformation': ('Mechanics illustration', [
        ('slide-2-image-5.gif', 'Large deformation under the same loading'),
    ]),
}
