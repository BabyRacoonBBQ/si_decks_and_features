"""English feature explanations and explicitly planned solution concepts.

Physics/coupling overview: StressThermal.pptx slide 1.
Feature scope: slides 2, 3 and 7. Future solution scope: slide 6.
The trace-mapping equations below are a proposed design, not a recovered
implementation or a claim about the proprietary GT-A implementation.
"""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parent
E = html.escape

# Purpose and primary result. These explain the feature, not its validation status.
SUMMARIES = {
    'Quasistatic equilibrium': ('Find the deformation of a structure under slowly applied loads, with inertia neglected.', 'Displacement, stress, strain and support reactions.'),
    'Linear buckling': ('Linearize stability about a loaded equilibrium state and find load factors at which the tangent stiffness becomes singular.', 'Critical load multipliers and normalized buckling mode shapes; mode amplitude is not a predicted physical displacement.'),
    'Post-buckling': ('Follow the nonlinear equilibrium path after a stability limit, accounting for the evolving deformation and load-carrying behavior.', 'Load–displacement response and deformed stress states. Imperfections and path-following controls affect the response.'),
    'Isotropic elasticity': ('Use the same elastic response in every material direction, typically parameterized by Young’s modulus and Poisson’s ratio.', 'Reversible stress–strain response.'),
    'Anisotropic elasticity': ('Represent directional stiffness using a constitutive tensor and a material orientation, including cubic, hexagonal and orthotropic models.', 'Orientation-dependent stress and deformation.'),
    'Viscous': ('Represent a rate-dependent stress response associated with deformation rate.', 'Stress evolution and time-dependent deformation for the selected viscosity model.'),
    'Viscoelastic': ('Combine elastic storage and viscous relaxation using a model such as Maxwell or standard linear solid.', 'Creep or stress relaxation and internal-state history.'),
    'Plastic': ('Allow irreversible strain once a yield condition is reached, with the chosen hardening law controlling subsequent response.', 'Plastic strain, residual deformation and updated stress.'),
    'Viscoplastic': ('Represent irreversible deformation whose rate depends on stress, temperature and internal state.', 'Viscoplastic strain and time-dependent stress redistribution.'),
    'Power-law creep': ('Describe accumulated inelastic strain under sustained stress using the selected stress- and temperature-dependent creep law.', 'Creep strain and long-term stress redistribution.'),
    'Swelling': ('Introduce a volumetric expansion strain associated with a prescribed material-state change.', 'Expansion and constraint-induced stress.'),
    'Cohesive damage': ('Represent progressive loss of interface traction as separation grows under a selected cohesive law.', 'Interface opening, traction and damage evolution.'),
    'Softening': ('Reduce the resisting stress or traction with continued deformation or damage after a peak response.', 'Post-peak response; regularization and discretization must be considered when interpreting localization.'),
    'Temperature-dependent parameters': ('Update material properties from the current temperature rather than treating them as constants.', 'Temperature-dependent constitutive response in the selected physics module.'),
    'Plane strain': ('Model a long structure with negligible out-of-plane strain while retaining the corresponding out-of-plane stress.', 'A two-dimensional displacement solution and the associated three-dimensional stress components.'),
    '3D solid': ('Resolve all three displacement components in a volumetric solid mesh.', 'Three-dimensional stress, strain and deformation.'),
    'Plane stress': ('Model a thin body whose out-of-plane stress components are negligible.', 'In-plane deformation with constitutive elimination of the out-of-plane stress.'),
    'Axisymmetric': ('Represent a body of revolution with geometry and loads independent of the circumferential coordinate.', 'Radial, axial and circumferential response from a meridional model.'),
    'Composite solid shell': ('Represent thin layered structures with a solid-shell formulation suited to membrane and bending behavior.', 'Layer-sensitive deformation and stress subject to the formulation’s kinematic assumptions.'),
    '3D Timoshenko composite beam': ('Represent a slender member with axial, bending, torsional and transverse-shear deformation.', 'Beam displacement, rotation and sectional response.'),
    'First-order elements': ('Interpolate the solution with linear shape functions within an element.', 'A discretized field whose accuracy depends on mesh resolution and element quality.'),
    'Second-order elements': ('Use quadratic interpolation with additional degrees of freedom to resolve curved or bending-dominated fields.', 'Higher-order displacement and derived stress fields.'),
    'Mixed mesh': ('Combine supported element topologies in a single analysis mesh.', 'A connected discrete model with compatible field transfer across element interfaces.'),
    'Thermal mismatch': ('Convert differences in thermal expansion and temperature into incompatible free strains across bonded materials.', 'Thermally induced stress, deformation and warpage.'),
    'Intrinsic stress': ('Introduce stress associated with material formation or processing independently of the current external load.', 'Residual stress and the deformation required to restore equilibrium.'),
    'Densification': ('Represent material shrinkage associated with an increase in density.', 'Shrinkage-induced strain and stress under constraint.'),
    'Grain growth': ('Represent the mechanical effect of changes in grain structure during processing.', 'Stress evolution associated with the selected grain-growth model.'),
    'Gravity force': ('Apply a body force proportional to material density and gravitational acceleration.', 'Gravity-induced displacement and stress.'),
    'Surface reflow': ('Represent stress and shape-related forces associated with surface reflow.', 'The response to the selected surface-reflow force model.'),
    'Edge dislocation': ('Represent the elastic disturbance associated with an edge-dislocation defect.', 'Localized displacement and stress around the defect.'),
    'Inverse piezoelectric effect': ('Convert an electric-field change into a mechanical constitutive contribution through piezoelectric coefficients.', 'Electrically induced deformation and stress.'),
    'Fluid surface tension': ('Apply interface forces arising from surface tension and interface geometry.', 'Capillary-force-induced stress and deformation.'),
    'Fluid pressure': ('Apply the mechanical action of fluid pressure to a solid boundary.', 'Pressure-induced displacement and stress.'),
    'Cohesive zipping': ('Represent an attractive interaction as nearby surfaces approach and join.', 'Surface closure and the associated deformation.'),
    'Phase change': ('Represent a transformation strain or property change associated with a material phase transition.', 'Transformation-induced stress and deformation.'),
    'Etch stress rebalancing': ('Re-establish mechanical equilibrium after removing material and exposing new boundaries.', 'Redistributed stress and deformation of the remaining structure.'),
    'Deposition stress rebalancing': ('Re-establish equilibrium after adding material, including any initial stress assigned to the deposited region.', 'Updated residual stress and deformation.'),
    'Geometric nonlinearity': ('Account for changes in geometry and rotation that alter equilibrium and strain measures.', 'A load-dependent tangent response and finite-deformation equilibrium.'),
    'Mechanical contact': ('Constrain interpenetration between interacting surfaces and apply the selected contact law.', 'Contact pressure, gap and surface motion; friction requires its own constitutive specification.'),
    'Crack analysis': ('Assess the mechanical effect of a crack or a defined fracture interface.', 'Crack-tip or interface response under the chosen fracture model.'),
    'Prescribed displacement': ('Fix selected displacement components on a point, boundary or named contact.', 'A constrained displacement field and the reaction forces required to enforce it.'),
    'Prescribed displacement rate': ('Drive a boundary by specifying the time rate of displacement.', 'A displacement history and the resulting stress response.'),
    'Traction': ('Apply a force per unit area with a specified direction on a surface.', 'Distributed boundary loading in the mechanical equilibrium equation.'),
    'Pressure boundary': ('Apply a normal compressive surface load with the selected sign convention.', 'Pressure-induced deformation and stress.'),
    'Point force': ('Apply a concentrated load at a specified point or associated degree of freedom.', 'Global deformation and stress; the immediate loading neighborhood may be singular or mesh-sensitive.'),
    'Reaction-force output': ('Recover forces associated with constrained displacement degrees of freedom.', 'Support reactions for force balance and load–displacement evaluation.'),
    'Moment': ('Apply a rotational loading resultant through a compatible boundary or element representation.', 'Bending or torsional response.'),
    'Symmetry': ('Restrict motion on a symmetry plane according to the assumed symmetry of geometry and loading.', 'A reduced-domain model with compatible displacement constraints.'),
    'Periodic boundary': ('Relate fields on corresponding boundaries of a repeating structure.', 'A periodic or prescribed macroscopic response from a representative domain.'),
    'Coupling boundary': ('Transfer or constrain boundary motion using another region or a global model.', 'A compatible local solution driven by the transferred boundary field.'),
    'Beam-plate coupling': ('Connect beam and plate representations while respecting their distinct displacement and rotation degrees of freedom.', 'Load transfer between reduced-dimensional structural models.'),
    'Variable boundary': ('Allow boundary data to vary with the specified position, time or controlling field.', 'A solution driven by nonuniform or evolving boundary conditions.'),
    'Steady-state thermal analysis': ('Solve the temperature distribution after heat storage ceases to change in time.', 'Temperature and heat flux satisfying heat-source and boundary balances.'),
    'Transient thermal analysis': ('Track temperature evolution while accounting for material heat storage.', 'Temperature and heat-flux histories from an initial state.'),
    'Conduction': ('Transfer heat down a temperature gradient within and between materials.', 'Conductive heat flux governed by thermal conductivity.'),
    'Convection': ('Exchange heat between a surface and a surrounding fluid through a heat-transfer coefficient.', 'Heat exchange driven by the surface-to-ambient temperature difference.'),
    'Radiation': ('Exchange thermal energy with the environment through surface radiation.', 'Temperature-dependent radiative heat loss or gain.'),
    'Thermal conductivity': ('Relate temperature gradient to heat flux using a scalar or directional conductivity tensor.', 'The spatial conduction response, including anisotropic heat spreading.'),
    'Heat storage': ('Use density and specific heat capacity to relate temperature rate to stored thermal energy.', 'Transient thermal inertia; volumetric heat capacity is density times mass-specific heat capacity.'),
    'Emissivity': ('Scale thermal radiation relative to an ideal black surface under the selected radiation model.', 'The surface’s radiative heat-exchange strength.'),
    'Applied heating': ('Prescribe a volumetric heat-source density inside the domain.', 'A temperature response driven by internal power generation.'),
    'Electrical heating': ('Convert electrical dissipation into a thermal source.', 'Joule heat-source density transferred to the thermal equation.'),
    'Prescribed temperature': ('Set the temperature at a boundary or specified location.', 'A thermal solution constrained by the imposed temperature.'),
    'Temperature ramps': ('Vary an imposed temperature over time according to a prescribed ramp.', 'Heating or cooling histories for thermal and coupled stress analysis.'),
    'Prescribed heat flux': ('Specify heat flow per unit area through a boundary.', 'A temperature response consistent with the imposed surface energy input or loss.'),
    'Contact power': ('Supply a total thermal power through a named contact according to the boundary distribution rule.', 'A boundary heat input whose integral matches the specified power.'),
    'Adiabatic boundary': ('Set the normal heat flux through a boundary to zero.', 'A thermally insulated boundary.'),
    'Convection boundary': ('Apply a surface heat balance using ambient temperature and a convection coefficient.', 'Convective boundary heat flux.'),
    'Radiation boundary': ('Apply radiative exchange between a surface and its defined surroundings.', 'A nonlinear boundary heat flux dependent on absolute temperature.'),
    'Thermal resistor': ('Represent a thermal connection with an assigned resistance between thermal states.', 'Heat flow driven by a temperature difference across the resistance.'),
    'Temperature continuity': ('Enforce equal temperature across an ideal bonded material interface.', 'A continuous interface temperature field.'),
    'Heat-flux continuity': ('Conserve normal heat flow across an interface without an interfacial heat source.', 'Balanced heat transfer between adjacent materials.'),
    'Interface thermal resistance': ('Allow a temperature jump across an interface proportional to its transmitted heat flux.', 'An interface temperature discontinuity and heat-transfer rate.'),
    'Thermomechanical': ('Transfer temperature to mechanics through thermal strain and temperature-dependent stiffness.', 'Temperature-driven displacement, stress and warpage.'),
    'Electrical current': ('Solve charge-current continuity in conducting regions, including the displacement-current term shown in the mode formulation.', 'Electric potential, electric field and conduction current density.'),
    'Electrostatic': ('Solve the potential created by a free-charge distribution in dielectric materials.', 'Electric potential and electric field.'),
    'Electrothermal': ('Transfer Joule heating to thermal analysis and use temperature to update electrical conductivity.', 'Coupled electric-potential, current-density and temperature fields.'),
    'Electromechanical': ('Transfer an electric-field change into a mechanical contribution through inverse piezoelectric coupling.', 'Electrically driven deformation and stress.'),
    'FEM mechanics': ('Discretize the weak form of mechanical equilibrium using finite-element shape functions.', 'An assembled mechanical residual and tangent system.'),
    'FVM thermal': ('Balance heat sources, storage and face fluxes over control volumes.', 'A conservative discrete temperature equation.'),
    'FVM electrical': ('Balance electric current across control-volume faces.', 'A conservative discrete potential equation.'),
    'TRBDF': ('Integrate time-dependent equations using a trapezoidal-rule/backward-differentiation scheme.', 'A time-discrete solution with step-size and convergence controls.'),
    'Newton': ('Linearize a nonlinear residual and update the solution until convergence criteria are met.', 'A converged nonlinear equilibrium or a reported convergence failure.'),
    'Direct solvers': ('Factor the assembled sparse matrix to solve a linear system.', 'A linear-system solution subject to conditioning and numerical tolerances.'),
    'Iterative solvers': ('Improve an approximate linear-system solution using an iteration and usually a preconditioner.', 'A solution meeting the selected residual tolerance.'),
    'ARPACK': ('Compute a requested subset of eigenpairs of a large sparse eigenproblem.', 'Selected eigenvalues and eigenvectors, including the buckling modes requested by a case.'),
    'MUMPS': ('Factor and solve sparse linear systems with a multifrontal direct solver.', 'Linear solves used by the configured analysis or eigenvalue transformation.'),
    'Shape functions': ('Interpolate fields and map nodal degrees of freedom to values inside an element.', 'Element-level field values and gradients for assembly and post-processing.'),
    'Material inheritance': ('Create a new material by inheriting a base material definition and overriding selected parameters.', 'A reusable material definition with explicit parameter differences.'),
    'Thermoelectromechanical coupling': ('Combine electrical dissipation, thermal transport and temperature-driven mechanical response.', 'Electric potential, temperature, displacement and stress for a coupled loading state.'),
    'Thermal resistance matrix': ('Relate multiple applied powers to temperature rises at multiple thermal ports.', 'A matrix containing self-heating and mutual thermal-coupling responses.'),
    'Stress analysis': ('Evaluate stress measures, principal values and directions from the mechanical solution.', 'Stress components, principal stresses and selected extrema.'),
    'Stress history': ('Record the change in stress across load, time or process steps.', 'A stress history for assessing redistribution and identifying peak loading states.'),
    'Field visualization': ('Display solved fields on the model, profiles or a deformation-scaled geometry.', 'Contour and profile views; deformation scaling is a display setting rather than a changed solution.'),
    'Field output': ('Write selected solution fields and derived quantities for inspection or downstream use.', 'Field datasets and profile tables with their physical meaning and units.'),
    'Stress-induced mobility enhancement': ('Use stress-dependent material relations to evaluate a mobility change.', 'A mobility-related response derived from the stress field and selected model.'),
    'Geometry transformations and vertex merging': ('Translate geometry or merge coincident vertices under the specified geometric rule.', 'Updated geometry and connectivity for subsequent modeling.'),
    'Tcl scripting': ('Compose a simulation workflow using Tcl commands, variables and reusable scripts.', 'A reproducible command sequence with controlled inputs and execution order.'),
    'Units': ('Associate explicit units with supported command values and maintain consistent physical quantities.', 'Correctly scaled inputs for geometry, loads, material properties and time.'),
    'Field-data import': ('Read an existing field dataset to initialize or continue an analysis.', 'An imported state, with field and mesh compatibility checked before continuation.'),
}

MODELS = {
    'Quasistatic equilibrium': (
        [('Mechanical equilibrium', '∇·σ + b = 0', 'u: displacement; σ: Cauchy stress; b: body-force density. The constitutive law connects stress to strain and material state.')],
        ['Define materials and mesh', 'Apply loads and displacement constraints', 'Solve for displacement u', 'Evaluate stress, strain and reactions']),
    'Steady-state thermal analysis': (
        [('Steady heat equation', '−∇·(k∇T) = Q', 'T: temperature; k: thermal conductivity (scalar or tensor); Q: volumetric heat-source density. This is the steady limit of the PPT heat equation.')],
        ['Define k and internal heating', 'Set thermal boundaries', 'Solve temperature T', 'Compute heat flux q = −k∇T']),
    'Transient thermal analysis': (
        [('Heat equation', 'ρcₚ ∂T/∂t − ∇·(k∇T) = Q', 'ρ: density; cₚ: heat capacity per unit mass; ρcₚ: volumetric heat capacity. Initial temperature and time-dependent boundary conditions complete the problem.')],
        ['Initialize temperature', 'Apply heating and boundary history', 'Advance temperature in time', 'Evaluate heat flux and thermal history']),
    'Electrical current': (
        [('Current continuity', '∇·(σₑ∇φ) = ∇·Jᴰ', 'φ: electric potential; σₑ: electrical conductivity; Jᴰ: displacement-current density.'),
         ('Field and current', 'E = −∇φ;  Jᶜ = σₑE;  Jᴰ = −∂(ε∇φ)/∂t', 'ε: dielectric permittivity. If displacement current is absent, the potential equation reduces to ∇·(σₑ∇φ) = 0.')],
        ['Define conductivity and electrical boundaries', 'Solve potential φ', 'Derive electric field E', 'Evaluate current density Jᶜ']),
    'Electrostatic': (
        [('Poisson equation', '∇·(ε∇φ) = −ρf', 'ρf: free-charge density; ε: dielectric permittivity; φ: electric potential.'),
         ('Electric field', 'E = −∇φ', 'Electrical potential or charge boundary conditions complete the electrostatic problem.')],
        ['Define permittivity and free charge', 'Apply electrostatic boundaries', 'Solve potential φ', 'Derive electric field E']),
    'Thermomechanical': (
        [('Thermal expansion increment', 'Δεᵗʰ ≈ αrel(T̄) ΔT I', 'αrel: relative thermal-expansion coefficient; T̄: representative temperature over the increment; I: identity tensor. The displayed relation is the isotropic approximation in the PPT.'),
         ('Temperature-dependent stiffness', 'C = C(T)', 'Temperature changes both free thermal strain and the constitutive stiffness used by mechanics.'),
         ('Mechanical equilibrium', '∇·σ + b = 0', 'Solve displacement subject to the transferred temperature and mechanical constraints.')],
        ['Solve thermal field T', 'Map temperature to mechanics', 'Update thermal strain and C(T)', 'Solve displacement and stress']),
    'Electrothermal': (
        [('Joule heat source', 'QJ = Jᶜ·E = σₑ(T)|E|²', 'The scalar expression assumes isotropic conductivity; the dot product remains valid for tensor conductivity.'),
         ('Thermal balance', 'ρcₚ ∂T/∂t − ∇·(k∇T) = QJ + Qother', 'The electrical dissipation becomes a volumetric thermal source.'),
         ('Temperature feedback', 'T → σₑ(T) → φ → E → Jᶜ', 'This is the feedback relationship shown in the PPT; the update schedule and convergence criteria are solver settings.')],
        ['Solve electrical potential', 'Compute E, Jᶜ and Joule heating', 'Solve temperature', 'Update σₑ(T) and repeat as required']),
    'Electromechanical': (
        [('Inverse piezoelectric contribution', 'Δσⱼᴵᴾ = −Σᵢ eᵢⱼ (Eᵢⁿᵉʷ − Eᵢᵒˡᵈ)', 'eᵢⱼ: piezoelectric coupling coefficients; j denotes the stress component in the constitutive representation. The sign follows the PPT convention.')],
        ['Solve electric field', 'Evaluate field increment ΔE', 'Form piezoelectric stress contribution', 'Solve mechanical equilibrium']),
    'Thermoelectromechanical coupling': (
        [('Electrical to thermal', 'QJ = Jᶜ·E', 'Electrical dissipation drives the heat equation.'),
         ('Thermal to mechanical', 'Δεᵗʰ ≈ αrel(T̄) ΔT I;  C = C(T)', 'Temperature drives expansion and updates material stiffness.'),
         ('Thermal to electrical', 'σₑ = σₑ(T)', 'Temperature may feed back into electrical conductivity. This flow composes the coupling paths in the PPT; it does not assert a monolithic three-field implementation.')],
        ['Electrical solution', 'Joule heating', 'Thermal solution', 'Thermal strain and stiffness update', 'Mechanical solution']),
}

PLANNED = [
    dict(id='trace-mapping', name='Trace Mapping', category='Solutions', module='Future Plan', status='TODO', case_ids=[], page='feature-trace-mapping.html', details=[]),
    dict(id='hybrid-bonding', name='Hybrid Bonding', category='Solutions', module='Future Plan', status='TODO', case_ids=[], page='feature-hybrid-bonding.html', details=[]),
    dict(id='vibration-analysis', name='Vibration Analysis', category='Solutions', module='Future Plan', status='TODO', case_ids=[], page='feature-vibration-analysis.html', details=[]),
]

CONTENT_CSS = '''
.feature-content{margin-top:24px}.feature-content .concept-card{background:white;border:1px solid #d5dfeb;border-radius:12px;padding:24px;margin:16px 0}
.feature-content .equation{font-family:Georgia,"Cambria Math",serif;font-size:1.35rem;line-height:1.8;background:#edf5f7;border-left:3px solid #16818b;padding:14px 18px;overflow-wrap:anywhere}
.feature-content .process{display:flex;flex-wrap:wrap;gap:12px;padding:0;list-style-position:inside;counter-reset:flow}
.feature-content .process li{list-style:none;flex:1 1 170px;background:#edf5f7;border:1px solid #cfdee6;border-radius:8px;padding:16px;counter-increment:flow}
.feature-content .process li:before{content:counter(flow) " → ";font-weight:bold;color:#087b86}.feature-content .planned-note{color:#725522;background:#fff4df;border-radius:8px;padding:12px 16px}
.feature-content .reference{font-size:.85rem;color:#657b8e}.feature-content li{margin:8px 0}.feature-content h3{margin-top:20px}
'''

def flow(steps):
    return '<ol class="process">'+''.join(f'<li>{E(s)}</li>' for s in steps)+'</ol>'

def equation(title, expression, explanation):
    return f'<h3>{E(title)}</h3><div class="equation" role="math" aria-label="{E(title)}">{E(expression)}</div><p>{E(explanation)}</p>'

def bullets(items):
    return '<ul>'+''.join(f'<li>{E(s)}</li>' for s in items)+'</ul>'

def future_content(name):
    intro='<p class="planned-note">Future Plan · Proposed capability. The workflow below describes the intended design, not a completed or validated implementation.</p>'
    if name=='Trace Mapping':
        return intro+'''<h2>Application background</h2><p>Package substrates and PCBs contain dense copper traces in dielectric layers. Resolving every trace with a conforming finite-element mesh can be expensive. Trace Mapping transfers the layout’s spatial copper distribution to a structural or thermal mesh so local material variation can be retained without meshing every trace edge.</p><h2>Planned workflow</h2>'''+flow([
            'Import ECAD layers and align units, axes and origins',
            'Calculate copper fraction on a source grid',
            'Intersect source cells with target FE elements',
            'Transfer copper fraction using overlap weights',
            'Assign effective material properties',
            'Solve thermal or mechanical response'])+'''<h2>Proposed mapping algorithm</h2><p>The PPT names a copper-fraction source grid and grid–FE overlap weighting. The following equations make that proposed design explicit; they are not a specification of the proprietary GT-A algorithm.</p>'''+equation(
            '1. Source copper fraction', 'fᵢ = V(Cu ∩ Gᵢ) / V(Gᵢ)',
            'Gᵢ is a source cell. For a constant-thickness layer this can be evaluated from in-plane overlap areas. Keep each physical layer separate.')+equation(
            '2. Conservative transfer', 'wₑᵢ = V(Eₑ ∩ Gᵢ);   fₑ = Σᵢ wₑᵢ fᵢ / V(Eₑ)',
            'Eₑ is a target element. This form assumes the source grid covers the whole target element. If coverage is incomplete, flag it or assign an explicit background material; do not silently renormalize the covered portion.')+equation(
            '3. Effective-property assignment', 'ρeff = fₑρCu + (1 − fₑ)ρdielectric',
            'Density is a volume mixture. Stiffness, conductivity and thermal expansion require a declared homogenization model and material orientation; copper fraction alone does not establish an accurate anisotropic constitutive law.')+'''<h2>Checks before release</h2>'''+bullets([
            'Preserve layer identity, units, coordinate alignment and material orientation.',
            'Require fractions between 0 and 1 and report uncovered or multiply covered volumes.',
            'For identical covered domains, compare Σₑ V(Eₑ)fₑ against the source copper volume.',
            'Check uniform-copper and uniform-dielectric limits, grid refinement and mesh independence.',
            'Compare mapped and explicitly resolved trace models for temperature, warpage and stress.'])+'''<h2>Outputs</h2><p>Element copper fraction, coverage diagnostics, assigned material parameters and a mapping report. Existing stress and thermal analysis provide the planned solution foundation.</p>'''
    if name=='Hybrid Bonding':
        return intro+'''<h2>Application background</h2><p>High-density chip-to-chip integration places closely spaced bonded interfaces under processing and thermal loads. Thermal-expansion mismatch, local deformation and interface separation can affect bond integrity. The planned solution connects stress analysis with interface mechanics.</p><h2>Planned workflow</h2>'''+flow([
            'Define bonded layers and interfaces','Apply processing or thermal loads',
            'Solve contact and stress','Evaluate interface opening and damage','Assess crack initiation or growth'])+'''<h2>Capability modules</h2><table><thead><tr><th>Module</th><th>Role</th><th>Plan</th></tr></thead><tbody><tr><td>Stress analysis</td><td>Resolve deformation and stress near the bond.</td><td>Existing foundation</td></tr><tr><td>Mechanical contact</td><td>Resolve interface closure and contact pressure.</td><td>Planned extension</td></tr><tr><td>Cohesive damage / softening</td><td>Relate traction to separation and progressive bond degradation.</td><td>Planned extension</td></tr><tr><td>Crack analysis</td><td>Evaluate fracture under the selected interface model.</td><td>Planned extension</td></tr></tbody></table><h2>Inputs and results</h2><p>Inputs include interface geometry, material properties, loading history and a calibrated interface law. Intended results include displacement, contact pressure, interface separation, stress and damage. A quantitative fracture prediction requires calibrated strength and fracture-energy parameters.</p><h2>Checks before release</h2>'''+bullets([
            'Validate contact closure and force balance with simple interface examples.',
            'Check traction–separation response and dissipated energy against the specified law.',
            'Study mesh sensitivity near interfaces and compare against a defined benchmark.'])
    return intro+'''<h2>Application background</h2><p>Chip, package and PCB assemblies can amplify motion near their resonant frequencies. The planned vibration capability helps identify resonance and estimate structural response under periodic excitation or a specified shock response spectrum.</p><h2>Frequency / Modal</h2>'''+equation(
        'Undamped free vibration', '(K − ω²M)φ = 0;   f = ω / (2π)',
        'K is stiffness, M is mass, φ is a mode shape, ω is angular frequency and f is frequency in Hz. Mode shapes are normalized patterns, not absolute displacement predictions.')+'''<h2>Harmonic Response</h2>'''+equation(
        'Steady sinusoidal response', '(K + iωC − ω²M) û = F̂',
        'C is a damping matrix. Complex displacement û describes response amplitude and phase at the excitation frequency. Damping and the excitation definition are required inputs.')+'''<h2>Response Spectrum</h2><p>Use modal frequencies, participation factors and a supplied excitation spectrum to estimate peak structural responses. The modal combination rule, damping and treatment of closely spaced modes must be specified. A spectrum-based peak estimate is not a reconstructed time history.</p><h2>Planned workflow</h2>'''+flow([
        'Define mass, stiffness and supports','Compute modes and participation',
        'Specify damping and excitation','Calculate harmonic or spectrum response','Evaluate displacement and stress'])+'''<h2>Checks before release</h2>'''+bullets([
        'Compare natural frequencies with analytical beam or plate examples.',
        'Check rigid-body modes, mesh convergence and modal normalization.',
        'Validate harmonic amplitude and phase on a damped oscillator.',
        'Verify spectrum interpolation, participation factors and the selected modal combination rule.'])

def content_html(feature):
    name=feature['name']
    if name in {f['name'] for f in PLANNED}:
        body=future_content(name)
        reference='Scope: StressThermal, slide 6. Equations and validation checks expand the proposed design.'
    else:
        if name not in SUMMARIES:
            raise ValueError('Missing feature explanation: '+name)
        purpose,result=SUMMARIES[name]
        body=f'<h2>What this feature does</h2><p>{E(purpose)}</p><h3>Primary result</h3><p>{E(result)}</p>'
        if name in MODELS:
            equations,steps=MODELS[name]
            body+='<h2>Governing relations</h2>'+''.join(equation(*item) for item in equations)
            body+='<h2>Calculation flow</h2>'+flow(steps)
            reference='Physics and coupling: StressThermal, slide 1. Explanations clarify variables and assumptions.'
        else:
            reference='Capability scope: StressThermal and the catalog feature records. This explanation does not change the recorded development or validation status.'
    return '<!-- feature-content:start --><section class="feature-content"><div class="concept-card">'+body+f'<p class="reference">{E(reference)}</p></div></section><!-- feature-content:end -->'

def register_planned(features):
    for planned in PLANNED:
        if not any(f['id']==planned['id'] for f in features):
            features.append(dict(planned, case_ids=[], details=[]))

def apply_to_existing():
    """Update feature content only; do not regenerate parent-thread case pages."""
    path=ROOT/'catalog-merged.json'
    data=json.loads(path.read_text(encoding='utf-8'))
    features=data['features']
    register_planned(features)
    template=(ROOT/features[0]['page']).read_text(encoding='utf-8')
    for f in features:
        page=ROOT/f['page']
        f.setdefault('related_cases',[])
        if page.exists():
            text=page.read_text(encoding='utf-8')
            text=re.sub(r'<!-- feature-content:start -->.*?<!-- feature-content:end -->','',text,flags=re.S)
            # Place the explanation before existing command records and case lists.
            main=text.index('<main>')
            insertion=text.find('<h2>',main)
            if insertion==-1:insertion=text.index('</main>',main)
            text=text[:insertion]+content_html(f)+text[insertion:]
        else:
            body=f'<a href="index.html#{f["id"]}">← Features</a><div class="eyebrow">Future Plan / Solutions</div><h1>{E(f["name"])}</h1><span class="badge todo">TODO</span>'+content_html(f)
            body+='<h2>Related cases <span class="count">(0)</span></h2>'
            for group in ['Feature tests','Application cases']:
                body+=f'<section class="related-case-group"><h3>{group} <span class="count">(0)</span></h3><p>No associated cases recorded.</p></section>'
            text=re.sub(r'<main>.*?</main>',lambda _: '<main>'+body+'</main>',template,flags=re.S)
            text=re.sub(r'<title>.*?</title>',f'<title>{E(f["name"])} · StressThermal</title>',text)
        if CONTENT_CSS not in text:text=text.replace('</style>',CONTENT_CSS+'</style>',1)
        page.write_text(text,encoding='utf-8')
    index=ROOT/'index.html'
    text=index.read_text(encoding='utf-8')
    text=re.sub(r'<!-- future-plan:start -->.*?<!-- future-plan:end -->','',text,flags=re.S)
    card='<!-- future-plan:start --><article class="card"><small>Future Plan</small><h3>Solutions</h3>'
    for f in PLANNED:
        card+=f'<div class="row" id="{f["id"]}"><span><a href="{f["page"]}">{E(f["name"])}</a></span><span class="badge todo">TODO</span></div>'
    card+='</article><!-- future-plan:end -->'
    # All existing cards are inside the final grid container.
    text=text.replace('</div></main>',card+'</div></main>',1)
    index.write_text(text,encoding='utf-8')
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Updated {len(features)} feature pages; case pages were not regenerated.')

if __name__=='__main__':
    apply_to_existing()
