__author__ = "Mikael Mortensen <mikaem@math.uio.no>"
__date__ = "2013-06-25"
__copyright__ = "Copyright (C) 2013 " + __author__
__license__  = "GNU Lesser GPL version 3 or any later version"

from ..NSfracStep import *
from ..Skewed2D import *

# Override some problem specific parameters
NS_parameters.update(
    nu = 0.1,
    T  = 10.0,
    dt = 0.05,
    use_krylov_solvers = True,
    print_velocity_pressure_convergence = True)

globals().update(NS_parameters)

def create_bcs(V, Q, mesh, **NS_namespace):
    # Create inlet profile by solving Poisson equation on boundary
    u_inlet = Expression("10*x[1]*(0.2-x[1])")
    bc0 = DirichletBC(V, 0, walls)
    bc1 = DirichletBC(V, u_inlet, inlet)
    bc2 = DirichletBC(V, 0, inlet)
    return dict(u0 = [bc1, bc0],
                u1 = [bc2, bc0],
                p  = [DirichletBC(Q, 0, outlet)])

def pre_solve_hook(mesh, V, **NS_namespace):
    Vv = VectorFunctionSpace(mesh, "CG", V.ufl_element().degree())
    uv = Function(Vv)
    return dict(uv=uv, Vv=Vv)
    
def temporal_hook(u_, p_, mesh, tstep, print_intermediate_info, 
                  uv, **NS_namespace):
    if tstep % print_intermediate_info == 0:
        print "Continuity ", assemble(dot(u_, FacetNormal(mesh))*ds())
    
    if tstep % plot_interval == 0:
        assign(uv.sub(0), u_[0])
        assign(uv.sub(1), u_[1])
        plot(uv, title='Velocity')
        plot(p_, title='Pressure')

def theend_hook(u_, p_, **NS_namespace):
    plot(u_, title='Velocity')
    plot(p_, title='Pressure')
