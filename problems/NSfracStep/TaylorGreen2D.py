__author__ = "Mikael Mortensen <mikaem@math.uio.no>"
__date__ = "2013-06-25"
__copyright__ = "Copyright (C) 2013 " + __author__
__license__  = "GNU Lesser GPL version 3 or any later version"

from ..NSfracStep import *

# Override some problem specific parameters
NS_parameters.update(
    nu = 0.01,
    T = 1.,
    dt = 0.001,
    Nx = 20, Ny = 20,
    folder = "taylorgreen2D_results",
    plot_interval = 1000,
    save_step = 10000,
    checkpoint = 10000,
    print_intermediate_info = 1000,
    compute_error = 1,
    use_krylov_solvers = True,
    velocity_degree = 1,
    pressure_degree = 1,
    krylov_report = False
)
NS_parameters['krylov_solvers'] = {'monitor_convergence': False,
                                   'report': False,
                                   'relative_tolerance': 1e-10,
                                   'absolute_tolerance': 1e-10}

def mesh(Nx, Ny, **params):
    return RectangleMesh(0, 0, 2, 2, Nx, Ny)

class PeriodicDomain(SubDomain):
    
    def inside(self, x, on_boundary):
        # return True if on left or bottom boundary AND NOT on one of the two corners (0, 2) and (2, 0)
        return bool((near(x[0], 0) or near(x[1], 0)) and 
              (not ((near(x[0], 0) and near(x[1], 2)) or 
                    (near(x[0], 2) and near(x[1], 0)))) and on_boundary)

    def map(self, x, y):
        if near(x[0], 2) and near(x[1], 2):
            y[0] = x[0] - 2.0
            y[1] = x[1] - 2.0
        elif near(x[0], 2):
            y[0] = x[0] - 2.0
            y[1] = x[1]
        else:
            y[0] = x[0]
            y[1] = x[1] - 2.0

constrained_domain = PeriodicDomain()

initial_fields = dict(
    u0='-sin(pi*x[1])*cos(pi*x[0])*exp(-2.*pi*pi*nu*t)',
    u1='sin(pi*x[0])*cos(pi*x[1])*exp(-2.*pi*pi*nu*t)',
    p='-(cos(2*pi*x[0])+cos(2*pi*x[1]))*exp(-4.*pi*pi*nu*t)/4.')

dpdx = ('sin(2*pi*x[0])*2*pi*exp(-4.*pi*pi*nu*t)/4.',
        'sin(2*pi*x[1])*2*pi*exp(-4.*pi*pi*nu*t)/4.')
        
def initialize(q_, q_1, q_2, VV, t, nu, dt, initial_fields, **NS_namespace):
    """Initialize solution. 
    
    Use t=dt/2 for pressure since pressure is computed in between timesteps.
    
    """
    for ui in q_:
        deltat = dt/2. if ui is 'p' else 0.
        vv = interpolate(Expression((initial_fields[ui]), t=t+deltat, nu=nu), VV[ui])
        q_[ui].vector()[:] = vv.vector()[:]
        if not ui == 'p':
            q_1[ui].vector()[:] = vv.vector()[:]
            deltat = -dt
            vv = interpolate(Expression((initial_fields[ui]), t=t+deltat, nu=nu), VV[ui])
            q_2[ui].vector()[:] = vv.vector()[:]
    q_1['p'].vector()[:] = q_['p'].vector()[:]

total_error = zeros(3)


def pre_solve_hook(velocity_degree, mesh, constrained_domain, **NS_namespace):

    #Vv = VectorFunctionSpace(mesh, "CG", velocity_degree)
    #Pv = FunctionSpace(mesh, "CG", pressure_degree)

    V5 = FunctionSpace(mesh, "CG", 5+velocity_degree,
            constrained_domain=constrained_domain)
    #P5 = FunctionSpace(mesh, "CG", 5+pressure_degree)

    #uv = Function(Vv)
    #uv_e = interpolate(u_e, V5)
    #pv_e = interpolate(p_e, P5)

    #error_u = [1e10]
    #error_p = [1e10]

    return dict(V5=V5) 


def temporal_hook(q_, t, nu, VV, dt, plot_interval, initial_fields, tstep, sys_comp, 
                  compute_error, V5, **NS_namespace):
    """Function called at end of timestep.    

    Plot solution and compute error by comparing to analytical solution.
    Remember pressure is computed in between timesteps.
    
    """
    #if tstep % plot_interval == 0:
        #plot(q_['u0'], title='u')
        #plot(q_['u1'], title='v')
        #plot(q_['p'], title='p')
        #interactive()
        
    if tstep % compute_error == 0:
        err = {}

        for i, ui in enumerate(sys_comp):
            deltat_ = dt/2. if ui is 'p' else 0.
            ue = Expression((initial_fields[ui]), t=t-deltat_, nu=nu)
            ue = interpolate(ue, V5) #VV[ui])
            uen = norm(ue.vector())
            #ue.vector().axpy(-1, q_[ui].vector())
            ue = project(ue - q_[ui], V5)
            error = norm(ue.vector()) /uen
            err[ui] = "{0:2.6e}".format(norm(ue.vector())/uen)
            total_error[i] += error*dt     
        if MPI.rank(mpi_comm_world()) == 0:
            print "Error is ", err, " at time = ", t 


def theend_hook(mesh, q_, t, dt, nu, VV, sys_comp, initial_fields, V5, **NS_namespace):
    final_error = zeros(len(sys_comp))
    for i, ui in enumerate(sys_comp):
        deltat = dt/2. if ui is 'p' else 0.
        ue = Expression((initial_fields[ui]), t=t-deltat, nu=nu)
        ue = interpolate(ue, V5) #VV[ui])
        uen = norm(ue.vector())
        #ue.vector().axpy(-1, q_[ui].vector())
        ue = project(ue - q_[ui], V5)
        final_error[i] = norm(ue.vector()) / uen
        
    hmin = mesh.hmin()
    if MPI.rank(mpi_comm_world()) == 0:
        print "hmin = {}".format(hmin)
    s0 = "Total Error:"
    s1 = "Final Error:"
    for i, ui in enumerate(sys_comp):
        s0 += " {0:}={1:2.6e}".format(ui, total_error[i])
        s1 += " {0:}={1:2.6e}".format(ui, final_error[i])
    if MPI.rank(mpi_comm_world()) == 0:
        print s0
        print s1
        print mesh.hmin()
