"""Plots for reconstruction of a mesh from point cloud
"""
import pdb
import numpy as np
import warnings
import os
import itertools
import scipy.io

from point_cloud import wavefront
from visualization import graphics
from kinematics import sphere
from dynamics import asteroid

view = {'azimuth': 16.944197132093564, 'elevation': 66.34177792039738,
        'distance': 2.9356815748114435, 
        'focalpoint': np.array([0.20105769, -0.00420018, -0.016934045])}

def cube_into_sphere(img_path):
    """Transform a cube into a sphere
    """
    vc, fc = wavefront.read_obj('./integration/cube.obj')
    vs, fs = wavefront.ellipsoid_mesh(2, 2, 2, density=10, subdivisions=0)
    
    
    mfig = graphics.mayavi_figure(offscreen=True)
    mesh = graphics.mayavi_addMesh(mfig, vc,fc)
    ms = mesh.mlab_source
    index = 0
    for ii in range(5):
        for jj, pt in enumerate(vs):
            index += 1
            filename = os.path.join(img_path, 'cube_sphere_' + str(index).zfill(6) + '.jpg')
            graphics.mlab.savefig(filename, magnification=4)
            mesh_param = wavefront.polyhedron_parameters(vc, fc)
            vc, fc = wavefront.radius_mesh_incremental_update(pt, vc, fc,
                                                              mesh_param,
                                                              max_angle=np.deg2rad(5))
            ms.reset(x=vc[:, 0], y=vc[:, 1], z=vc[:, 2], triangles=fc)
            graphics.mayavi_addPoint(mfig, pt)
        
        vc, fc = wavefront.mesh_subdivide(vc, fc, 1)
        ms.reset(x=vc[:, 0], y=vc[:, 1], z=vc[:, 2], triangles=fc)

    return 0

def sphere_into_ellipsoid(img_path):
    """See if we can turn a sphere into an ellipse by changing the radius of
    vertices
    
    The point cloud (ellipse) should have more points than the initial mesh.
    When the intial mesh is coarse the resulting mesh will also be heavily faceted, but this will avoid the big holes, and large changes in depth
    """

    # define the sphere
    vs, fs = wavefront.ellipsoid_mesh(1, 1, 1, density=20, subdivisions=1)
    ve, fe = wavefront.ellipsoid_mesh(2, 3, 4, density=20, subdivisions=1)
    
    mfig = graphics.mayavi_figure(offscreen=True)
    mesh = graphics.mayavi_addMesh(mfig, vs, fs)
    ms = mesh.mlab_source
    index = 0
    # in a loop add each vertex of the ellipse into the sphere mesh
    for jj in range(2):
        for ii, pt in enumerate(ve):
            index +=1
            filename = os.path.join(img_path, 'sphere_ellipsoid_' + str(index).zfill(6) + '.jpg')
            graphics.mlab.savefig(filename, magnification=4)
            mesh_param = wavefront.polyhedron_parameters(vs, fs)
            vs, fs = wavefront.radius_mesh_incremental_update(pt, vs,fs,
                                                              mesh_param,
                                                              max_angle=np.deg2rad(10))
            ms.reset(x=vs[:,0], y=vs[:,1], z=vs[:,2], triangles=fs)
            graphics.mayavi_addPoint(mfig, pt)
    
        vs, fs = wavefront.mesh_subdivide(vs, fs,  1)
        ms.reset(x=vs[:,0], y=vs[:,1], z=vs[:,2], triangles=fs)

    return 0

def castalia_reconstruction(img_path):
    """Incrementally modify an ellipse into a low resolution verision of castalia
    by adding vertices and modifying the mesh
    """
    density = 20
    subdivisions = 1

    surf_area = 0.05
    factor = 1
    radius_factor = 0.05

    # load a low resolution ellipse to start
    ast = asteroid.Asteroid('castalia', 0, 'obj')
    ve, fe = wavefront.ellipsoid_mesh(ast.axes[0]*0.75, 
                                            ast.axes[1]*0.75,
                                            ast.axes[2]*0.75,
                                            density=density,
                                            subdivisions=subdivisions)
    # truth model from itokawa shape model
    vc, fc = ast.V, ast.F
    # sort the vertices in in order (x component)
    # vc = vc[vc[:, 0].argsort()]

    # both now into spherical coordinates
    ve_spherical = wavefront.cartesian2spherical(ve)
    vc_spherical = wavefront.cartesian2spherical(vc)

    # loop and create many figures
    mfig = graphics.mayavi_figure(offscreen=True)
    mesh = graphics.mayavi_addMesh(mfig, ve, fe)
    ms = mesh.mlab_source
    index = 0
    # pdb.set_trace()
    for ii, pt in enumerate(vc_spherical):
        index +=1
        filename = os.path.join(img_path, 'castalia_reconstruct_' + str(index).zfill(7) + '.jpg')
        graphics.mlab.savefig(filename, magnification=4)
        ve_spherical, fc = wavefront.spherical_incremental_mesh_update(pt,ve_spherical,fe,
                                                                       surf_area=surf_area,
                                                                       factor=factor,
                                                                       radius_factor=radius_factor)
        
        # back to cartesian
        ve_cartesian = wavefront.spherical2cartesian(ve_spherical)
        ms.reset(x=ve_cartesian[:, 0], y=ve_cartesian[:, 1], z=ve_cartesian[:, 2], triangles=fc)
        graphics.mayavi_addPoint(mfig, wavefront.spherical2cartesian(pt), radius=0.01 )
            
    
    return 0

def castalia_reconstruction_factor_tuning(img_path):
    """ Vary both the surface area and radius factor to see the effect
    """
    density = 20
    subdivisions = 1

    surf_area = np.array([0.01, 0.05, 0.1, 0.5, 1.0])
    factor = 1
    radius_factor = np.array([0.01, 0.05, 0.1, 0.5, 1.0, 5, 10])

    # load a low resolution ellipse to start
    ast = asteroid.Asteroid('castalia', 0, 'obj')
    ve, fe = wavefront.ellipsoid_mesh(ast.axes[0]*0.75, 
                                            ast.axes[1]*0.75,
                                            ast.axes[2]*0.75,
                                            density=density,
                                            subdivisions=subdivisions)
    # truth model from itokawa shape model
    vc, fc = ast.V, ast.F
    # sort the vertices in in order (x component)
    # vc = vc[vc[:, 0].argsort()]

    # both now into spherical coordinates
    ve_spherical = wavefront.cartesian2spherical(ve)
    vc_spherical = wavefront.cartesian2spherical(vc)

    # loop and create many figures
    mfig = graphics.mayavi_figure(offscreen=True)
    mesh = graphics.mayavi_addMesh(mfig, ve, fe)
    ms = mesh.mlab_source
    
    graphics.mayavi_points3d(mfig, vc, scale_factor=0.01)
    ve_s = ve_spherical.copy()

    for sa, rf in itertools.product(surf_area, radius_factor):
        index = 0
        filename = os.path.join(img_path, 'castalia_reconstruct_' + 'sa=' + str(sa).replace('.','') + '_rf=' + str(rf).replace('.','') + '.jpg')
        for ii, pt in enumerate(vc_spherical):
            ve_s, fc = wavefront.spherical_incremental_mesh_update(pt,ve_s,fe,
                                                                   surf_area=sa,
                                                                   factor=factor,
                                                                   radius_factor=rf)
            
            # back to cartesian
            ve_c = wavefront.spherical2cartesian(ve_s)

        ms.reset(x=ve_c[:, 0], y=ve_c[:, 1], z=ve_c[:, 2], triangles=fc)
        graphics.mayavi_addTitle(mfig, 'SA={} RF={}'.format(sa, rf), color=(0, 0, 0))
        graphics.mlab.savefig(filename, magnification=4)

def sphere_into_ellipsoid_spherical_coordinates(img_path):
    """See if we can turn a sphere into an ellipse by changing the radius of
    vertices in spherical coordinates
    
    The point cloud (ellipse) should have the same number of points than the initial mesh.
    """
    surf_area = 0.15
    factor = 1
    radius_factor = 0.15

    # define the sphere
    # vs, fs = wavefront.ellipsoid_mesh(0.5, 0.5, 0.5, density=10, subdivisions=1)
    # ve, fe = wavefront.ellipsoid_mesh(1,2, 3, density=10, subdivisions=1)
    
    # import the sphere and ellipsoid from matlab files
    sphere_data = scipy.io.loadmat('./data/sphere_distmesh.mat')
    ellipsoid_data = scipy.io.loadmat('./data/ellipsoid_distmesh.mat')

    vs, fs = sphere_data['v'], sphere_data['f']

    ve, fe = ellipsoid_data['v'], ellipsoid_data['f']

    # convert to spherical coordinates
    vs_spherical = wavefront.cartesian2spherical(vs)
    ve_spherical = wavefront.cartesian2spherical(ve)

    mfig = graphics.mayavi_figure(offscreen=True)
    mesh = graphics.mayavi_addMesh(mfig, vs, fs)
    ms = mesh.mlab_source
    index = 0

    # graphics.mayavi_points3d(mfig, vs, color=(1, 0, 0))
    # graphics.mayavi_points3d(mfig, ve, color=(0, 1, 0))
    # in a loop add each vertex of the ellipse into the sphere mesh
    np.random.shuffle(ve_spherical)
    for ii, pt in enumerate(ve_spherical):
        index +=1
        filename = os.path.join(img_path, 'sphere_ellipsoid_' + str(index).zfill(6) + '.jpg')
        graphics.mlab.savefig(filename, magnification=4)
        vs_spherical, fs = wavefront.spherical_incremental_mesh_update(mfig, pt, vs_spherical,fs,
                                                                surf_area=surf_area,
                                                                factor=factor,
                                                                radius_factor=radius_factor)
        # convert back to cartesian for plotting

        vs_cartesian = wavefront.spherical2cartesian(vs_spherical)
        ms.reset(x=vs_cartesian[:,0], y=vs_cartesian[:,1], z=vs_cartesian[:,2], triangles=fs)
        graphics.mayavi_addPoint(mfig, wavefront.spherical2cartesian(pt))
        
    return 0

if __name__ == "__main__":
    img_path = '/tmp/mayavi_figure'
    if not os.path.exists(img_path):
        os.makedirs(img_path)

    # cube_into_sphere(img_path)
    # sphere_into_ellipsoid(img_path)
    # castalia_reconstruction(img_path)
    sphere_into_ellipsoid_spherical_coordinates(img_path)
    # castalia_reconstruction_factor_tuning(img_path)
