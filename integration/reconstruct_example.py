# Reconstruction example and testing

from visualization import graphics
from point_cloud import wavefront
from lib import surface_mesh

from kinematics import attitude
import numpy as np
import scipy.io

import pdb

# load data from sphere and ellipsoid
# sphere_data = scipy.io.loadmat('./data/sphere_distmesh.mat')
# ellipsoid_data = scipy.io.loadmat('./data/ellipsoid_distmesh.mat')
# vs, fs = sphere_data['v'], sphere_data['f']
# ve, fe = ellipsoid_data['v'], ellipsoid_data['f']

# vs, f = wavefront.ellipsoid_mesh(0.5, 0.5, 0.5, density=20, subdivisions=1)
# ve, fe = wavefront.ellipsoid_mesh(1, 1, 1, density=10, subdivisions=1)
sphere= surface_mesh.SurfMesh(0.5, 0.5, 0.5, 10, 0.05, 0.5)
vs, fs = sphere.verts(), sphere.faces()

# convert all vertices to spherical coordinates
v_spherical = wavefront.cartesian2spherical(vs);
# ve_spherical = wavefront.cartesian2spherical(ve);

mfig = graphics.mayavi_figure()
# vc, f = wavefront.read_obj('./integration/cube.obj')
# v_spherical = wavefront.cartesian2spherical(vc)

# mesh_param = wavefront.polyhedron_parameters(v, f)
pt = np.array([1, 0, 0])
pt_spherical = wavefront.cartesian2spherical(pt)

vert_sigma = np.ones(v_spherical.shape[0])

nv_spherical, nf = wavefront.spherical_incremental_mesh_update(mfig, pt_spherical, v_spherical, fs,
                                                                vert_sigma,
                                                                surf_area=0.2,
                                                                a=0.5,delta=0.1)

# convert back to cartesian
nv = wavefront.spherical2cartesian(nv_spherical)

# view the mesh
graphics.mayavi_addMesh(mfig, nv, nf, representation='surface')
graphics.mayavi_addPoint(mfig, pt)
