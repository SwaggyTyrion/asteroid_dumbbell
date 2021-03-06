"""Testing out Blender Python API

First you'll need to build Blender using the script in utilities/build_blender.sh

Then you can try and API instructions at https://docs.blender.org/api/2.78b/info_quickstart.html

Hopefully this works
"""
import os
import bpy, _cycles
import numpy as np
import mathutils
import pdb
import h5py
import cv2
from kinematics import attitude
output_path = 'visualization/blender'

from visualization import blender_camera

# fixed rotation from SC frame to camera frame
# the camera in Blender is aligned with teh -z axis (view direction)
# blender cam x axis, y axis are aligned with teh spacecraft x, y axes
R_sc2bcam = np.array([[0, -1, 0], 
                      [0, 0, 1],
                      [-1, 0, 0]])

def print_object_locations():
    r"""Print out object properties for all the objects in a Blender scene

    This function will output all the positions of the objects in the scene.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Other Parameters
    ----------------
    None

    See Also
    --------

    Notes
    -----

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu

    References
    ----------

    .. [1] Blender Python API - https://docs.blender.org/api/2.78b/

    """
    for object in bpy.data.objects:
        print("{0} is at: {1}".format(object.name, str(object.location)))


def cylinder_between(x1, y1, z1, x2, y2, z2, r):
    """Draw a cylinder between points in Blender

    Given an already setup Blender scene, this function will draw a cyclinder
    between two points.

    Inputs :
    --------
    x1, y1, z1 : float
        Start of cyclinder in the blender world frame
    x2, y2, z2 : float
        End of cyclinder in blender world/inertial frame
    r : float
        radius of the cyclinder

    Returns :
    ---------
    None

    """

    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1    
    dist = np.sqrt(dx**2 + dy**2 + dz**2)

    bpy.ops.mesh.primitive_cylinder_add(
        radius = r, 
        depth = dist,
        location = (dx/2 + x1, dy/2 + y1, dz/2 + z1)   
    ) 

    phi = np.arctan2(dy, dx) 
    theta = np.arccos(dz/dist) 

    bpy.context.object.rotation_euler[1] = theta 
    bpy.context.object.rotation_euler[2] = phi 

def look_at(camera, point):
    r"""Ensure camera is pointing at object

    This function will ensure that within a blender scene that the camera is always pointed at the object

    Parameters
    ----------
    camera : blender object
        camera object
    point : blender point object
        the object to look at

    Returns
    -------
    None

    Other Parameters
    ----------------
    None

    Raises
    ------
    None

    See Also
    --------

    Notes
    -----

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu

    References
    ----------

    """ 
    
    loc_camera = camera.matrix_world.to_translation()

    direction = point - loc_camera

    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()

def camera_constraints(camera_obj, target_obj):
    """Create a constraint to point the camera at a specific object

    """

    # this sets a constraint for the camera to track a specific object
    cam_con = camera_obj.constraints.new('TRACK_TO')
    cam_con.target = target_obj
    cam_con.track_axis = 'TRACK_NEGATIVE_Z'
    cam_con.up_axis = 'UP_Y'

def load_asteroid(asteroid='itokawa_low'):
    """Load the desired asteroid

    Import the wavefront model of an asteroid

    Parameters : 
    ------------
    asteroid : string
        Filename and object name of the asteroid. 
        The wavefront file should be in the subdirectory ./data/
        You can generate new models by using the SBMT tool
        http://sbmt.jhuapl.edu/index.html

    Returns :
    ---------
    itokawa_obj : blender object
        Blender object that defines the asteroid

    """

    # import OBJ model
    bpy.ops.import_scene.obj(filepath=os.path.join('data',asteroid + '.obj'))

    itokawa_obj = bpy.data.objects[asteroid]
    itokawa_obj.scale = [1, 1, 1] 

    itokawa_obj.location.x = 0
    itokawa_obj.location.y = 0
    itokawa_obj.location.z = 0

    itokawa_obj.rotation_euler = mathutils.Euler((0, 0, 0), 'XYZ')

    bpy.context.scene.update()
    # set the material properties for the asteroid to match something realistic
    
    return itokawa_obj

def reset_scene():
    """Reset blender scene and remove all objects

    This function will reset the blender scene and delete all the objects

    """
    bpy.ops.wm.read_factory_settings(use_empty=True)

    for scene in bpy.data.scenes:
        for obj in scene.objects:
            scene.objects.unlink(obj)

    # only worry about data in the startup scene
    for bpy_data_iter in (
            bpy.data.objects,
            bpy.data.meshes,
            bpy.data.lamps,
            bpy.data.cameras,
            ):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data)

        
def blender_init(render_engine='BLENDER', 
                 resolution=[537,244],
                 fov=[2.93,2.235],
                 focal_length=167.35, 
                 asteroid_name='itokawa_low'):
    r"""Initialize the Blender scene for a camera around an asteroid

    This function will initialize the objects for a scene involving a camera,
    asteroid, and light source

    Parameters
    ----------
    render_engine : string
        Option to choose the type of rendering engine
            'BLENDER' - Default Blender render - fast
            'CYCLES' - Better rendering at the expense of speed/computation
    resolution : list or array_like
        The x,y pixel resolution of the resulting output image.
        The default matches the MSI camera on NEAR
    fov : list or array_like
        Field of View of the camera sensor in degrees - default is chosen to math NEAR 
    focal_length : float
        Focal length of camera in millimeters

    Returns
    -------
    camera : Blender camera
        Camera which lets you set camera properties
    camera_obj : Blender object
        Camera object - move it/rotation
    lamp : Blender Lamp
        Use to set lamp specific properties
    lamp_obj : Blender object
        Use to move and position
    itokawa_obj : Blender object
        Asteroid object
    scene : Blender scene
        Use to set general parameters for rendering

    See Also
    --------
    blender_example : Example for rendering an image 

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu

    """
    # setup the scene
    bpy.ops.wm.read_homefile()
    # start new empty scene
    scene = bpy.context.scene

    # delete the cube
    bpy.data.objects['Cube'].select = True
    bpy.ops.object.delete()
    
    # empty object for camera tracking purposes
    empty = bpy.data.objects.new('Empty', None)
    bpy.context.scene.objects.link(empty)
    bpy.context.scene.update()
    
    itokawa_obj = load_asteroid(asteroid=asteroid_name)

    # render options
    bpy.data.worlds['World'].horizon_color = [0, 0, 0]
    bpy.types.UnitSettings.system = 'METRIC'
    bpy.types.UnitSettings.scale_length = 1e3

    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    if render_engine == 'BLENDER':
        scene.render.engine = 'BLENDER_RENDER'
    else:
        scene.render.engine = 'CYCLES'

    # setup the camera
    camera_obj = bpy.data.objects['Camera']
    camera = bpy.data.cameras['Camera']
    camera.angle_x = np.deg2rad(fov[0])
    camera.angle_y = np.deg2rad(fov[1])
    camera.lens = focal_length# focal length in mm
    camera_obj.rotation_mode = 'XYZ'
    

    # setup the lamp 
    lamp = bpy.data.lamps['Lamp']
    lamp_obj = bpy.data.objects['Lamp']
    lamp.type = 'SUN'
    lamp.energy = 0.8
    lamp.use_specular = False
    lamp.use_diffuse = True
    
    # use spiceypy here to determine location of the light source
    lamp_obj.location.x = -5
    lamp_obj.location.y = 0
    lamp_obj.location.z = 1
    
    lamp_con = lamp_obj.constraints.new('TRACK_TO')
    lamp_con.target = itokawa_obj
    lamp_con.track_axis = 'TRACK_NEGATIVE_Z'
    lamp_con.up_axis = 'UP_Y'
    
    # set cuda device if available
    if len(_cycles.available_devices()) > 1:
        bpy.context.user_preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
        bpy.context.user_preferences.addons['cycles'].preferences.devices[0].use = True
        bpy.context.scene.cycles.device = 'GPU'

    bpy.context.scene.update()
    return (camera_obj, camera, lamp_obj, lamp, itokawa_obj, scene)

def blender_example():
    """Example to render an image
    
    This is a function that will render and image from Blender. 
    It serves as a benchmark that should hopefully always work
    """

    bpy.ops.wm.read_homefile() 
    scene = bpy.context.scene

    # delete the cube
    bpy.data.objects['Cube'].select = True
    bpy.ops.object.delete()
    
    # # delete default lamp
    # bpy.data.objects['Lamp'].select = True
    # bpy.ops.object.delete()

    # import OBJ model
    bpy.ops.import_scene.obj(filepath='data/itokawa_high.obj')

    # add a ground plane
    # add_plane = bpy.ops.mesh.primitive_plane_add
    # add_cube = bpy.ops.mesh.primitive_cube_add
    # cube = bpy.data.objects['Cube']
    # bpy.ops.object.camera_add()
    # bpy.ops.object.lamp_add()

    # set scene render options
    scene.render.resolution_x = 800
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    # scene.render.filepath = 'visualization/blender/'
    scene.render.engine = 'BLENDER_RENDER'
    # scene.render.engine = 'CYCLES'


    camera_obj = bpy.data.objects['Camera']
    camera = bpy.data.cameras['Camera']
    
    empty = bpy.data.objects.new('Empty', None)
    bpy.context.scene.objects.link(empty)
    bpy.context.scene.update()

    # new sun lamp
    # lamp = bpy.data.lamps.new('Lamp', 'SUN')
    # lamp_obj = bpy.data.objects.new('Lamp', lamp)
    # scene.objects.link(lamp_obj)
    # lamp_obj.select = True
    # scene.objects.active = lamp_obj
    lamp = bpy.data.lamps['Lamp'] 
    lamp_obj = bpy.data.objects['Lamp']
    
    lamp.type = 'SUN'
    lamp.energy = 0.8
    lamp.use_specular = False
    lamp.use_diffuse = True

    itokawa_obj = bpy.data.objects['itokawa_high']
    itokawa_obj.scale = [1,1,1]
    
    bpy.types.UnitSettings.system = 'METRIC'
    bpy.types.UnitSettings.scale_length = 1e3
    bpy.data.worlds['World'].horizon_color = [0, 0, 0]

    # draw cylinders for axes
    # cylinder_between(0, 0, 0, 5, 0, 0, 0.01)
    # cylinder_between(0, 0, 0, 0, 5, 0, 0.01)
    # cylinder_between(0, 0, 0, 0, 0, 5, 0.01)

    # delete the cube
    num_steps = 10
    time = np.arange(0, num_steps, 1)

    itokawa_obj.location.x = 0
    itokawa_obj.location.y = 0
    itokawa_obj.location.z = 0
    
    # set camera properties to match NEAR MSI
    camera.angle_x = np.deg2rad(2.93)
    camera.angle_y = np.deg2rad(2.25)
    # camera.sensor_height = 
    # camera.sensor_width = 
    camera.lens = 167.35 # focal length in mm

    camera_obj.location.x = 0
    camera_obj.location.y = -2
    camera_obj.location.z = 0


    con = camera_obj.constraints.new('TRACK_TO')
    con.target = itokawa_obj
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'

    # camera.rotation_euler.x = -90
    # camera.rotation_euler.y = 0
    # camera.rotation_euler.z = 0

    lamp_obj.location.x = 5
    lamp_obj.location.y = 0
    lamp_obj.location.z = 1
    
    lamp_obj.rotation_mode = 'XYZ'
    lamp_obj.rotation_euler = np.deg2rad([82, -10, 89])
    for ii, t in enumerate(time):
        # itokawa_obj.rotation_euler.z = 360 / (12.132 * 3600) * t
        camera_obj.location.x = 3* np.cos(t * 2*np.pi/num_steps)
        camera_obj.location.y = 3* np.sin(t * 2*np.pi/num_steps)

        camera_obj.location.z = 0

        # look_at(camera_obj, itokawa_obj.matrix_world.to_translation())
        # center_camera(camera_obj, mathutils.Vector([0, 0, 0]))

        scene.render.filepath = os.path.join(output_path, 'cube_' + str(ii)  + '.png')
        bpy.ops.render.render(write_still=True, use_viewport=True)

    for object in bpy.data.objects:
        print(object.name + " is at location " + str(object.location))

    
    print("Itokawa Size: ", end='')
    print(itokawa_obj.dimensions)

    return 0

def blender_render(name, scene, save_file=False):
    """Call this function to render the current scene and output the pixels
    
    This function will render an image or save the image data to a variable.

    In order to save to pixels you need to modify the source code for Blender 
    and recompile

    """
    
    if save_file:
        scene.render.filepath = os.path.join(output_path + '/' + name + '.png')
        bpy.ops.render.render(write_still=True)

    else:
        # need to modify the source for this to work
        # https://blender.stackexchange.com/questions/69230/python-render-script-different-outcome-when-run-in-background/81240#81240
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links

        # clear default nodes
        for n in tree.nodes:
            tree.nodes.remove(n)

        # create input render layer node
        rl = tree.nodes.new('CompositorNodeRLayers')
        
        # output node
        v = tree.nodes.new('CompositorNodeViewer')
        v.use_alpha = True

        # create a link
        links.new(rl.outputs[0], v.inputs[0])

        bpy.ops.render.render()

        img_data = bpy.data.images['Viewer Node'].pixels


def driver(sc_pos=[-2,0,0], 
           R_sc2ast=np.eye(3), 
           theta_ast=0, 
           sun_position=[-5, 0, 0], 
           filename='test'):
    r"""Generate a blender render given a camera position and orientation

    Generate a single image given a known position and orientation of the camera/spacecraft


    Parameters
    ----------
    sc_pos : (3,) array_like and float
        Position of the spacecraft/camera in the inertial frame (blender world coordinates)
        The units are in kilometers (1 Blender unit is 1 km)
    R_sc2ast : (3, 3) numpy array of float
        Rotation matrix which transforms vectors in teh spacecraft body frame to the inertial frame.
        The camera is rotated to be assumed to point along the body frame +X axis
    theta_ast : float
        Angle of rotation about z axis of the asteroid at current time
    filename : string
        Name of PNG file to save the rendered image

    Returns
    -------
    None

    Notes
    -----
    To transform vectors from the camera frame to the inertial/world frame

    .. math:: R_{I2B} = R_{S2I} * R_{B2S} 

    Rotation operations in blender are from the object/body frame to the
    inertial frame.  Therefore, in order to rotate an object with respect to
    the inertial frame you'll need to use the transpose.  Blender uses the same
    standard as most of the dynamics/papers, except for visualization we want
    the opposite.

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu

    References
    ----------
    This relies on the Blender Python Module.

    .. [1] https://wiki.blender.org/index.php/User:Ideasman42/BlenderAsPyModule 
    .. [2] Look at utilities/build_blender.sh for automatic building 

    Examples
    --------
    An example of how to use the function

    """  

    # initialize the scene
    camera_obj, camera, lamp_obj, lamp, itokawa_obj, scene = blender_init('BLENDER')

    # move camera and asteroid 
    camera_obj.location = sc_pos
    lamp_obj.location = sun_position
    
    # rotate asteroid
    itokawa_obj.rotation_euler = mathutils.Euler((0, 0, theta_ast), 'XYZ')

    # rotate the camera
    R_i2bcam = R_sc2ast.T.dot(np.array(R_sc2bcam.T))
    rot_euler = mathutils.Matrix(R_i2bcam).to_euler('XYZ')
    camera_obj.rotation_euler = rot_euler
    bpy.context.scene.update()
    # look_at(camera_obj, itokawa_obj.matrix_world.to_translation())

    # render an image from the spacecraft at this state
    # blender_render(filename,scene, True)
    scene.render.filepath = os.path.join(output_path + '/' + filename + '.png')
    bpy.ops.render.render(write_still=True)

def vertical_landing():
    """Example of vertical descent to surface

    This function just generates a bunch of images as the camera moves
    toward the surface

    """
    

    radius = np.arange(-10, -1, 0.1)
    theta = np.linspace(0, np.pi/2, len(radius))
    with h5py.File('./data/img_data.hdf5', 'w') as img_data:
        # define a dataset to store all the imagery
        vert_landing = img_data.create_dataset("vertical_landing", (244, 537, 3, len(radius)), dtype='uint8')
        # define the trajectory
        for ii,r in enumerate(radius):
            sc_pos = np.array([r, 0, 0])
            filename = 'test' + str.zfill(str(ii), 4)
            driver(sc_pos=sc_pos, R_sc2ast=np.eye(3), theta_ast=theta[ii], filename=filename)
            
            # read the image and store in HDF5 file
            img = cv2.imread('./visualization/blender/' + filename + '.png')

            vert_landing[:, :, :, ii] = img
        # close the file

def gen_image(sc_pos, R_sc2inertial, theta_ast, 
              camera_obj, camera, lamp_obj, lamp, itokawa_obj, scene, 
              sun_position=[-5, 0, 1], filename='test'):
    r"""This will generate a blender render given a camera position and
    orientation

    Generate a single image given a known position and orientation of the
    camera/spacecraft. The image is returned as an output.

    Parameters
    ----------
    sc_pos : (3,) array_like and float Position of the spacecraft/camera in the
    inertial frame (blender world coordinates) The units are in kilometers (1
    Blender unit is 1 km)
    R_sc2ast : (3, 3) numpy array of float
        Rotation matrix which transforms vectors in teh spacecraft body frame
        to the inertial frame.
        The camera is rotated to be assumed to point along the body frame +X axis
    theta_ast : float
        Angle of rotation about z axis of the asteroid at current time
    filename : string
        Name of PNG file to save the rendered image

    Returns
    -------
    img : np.array_
        Blender saves an image then OpenCV reads it and passes it back,
        same image is overwritten the next step



    Notes
    -----
    To transform vectors from the camera frame to the inertial/world frame

    .. math:: R_{I2B} = R_{S2I} * R_{B2S} 

    Rotation operations in blender are from the object/body frame to the
    inertial frame.  Therefore, in order to rotate an object with respect to
    the inertial frame you'll need to use the transpose.  Blender uses the same
    standard as most of the dynamics/papers, except for visualization we want
    the opposite.

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu

    References
    ----------
    This relies on the Blender Python Module.

    .. [1] https://wiki.blender.org/index.php/User:Ideasman42/BlenderAsPyModule 
    .. [2] Look at utilities/build_blender.sh for automatic building 


    """  
    
    # move camera and asteroid 
    camera_obj.location = sc_pos
    lamp_obj.location = sun_position
    
    # rotate asteroid
    itokawa_obj.location = [0, 0, 0]
    itokawa_obj.rotation_euler = mathutils.Euler((0, 0, theta_ast), 'XYZ')

    # rotate the camera
    R_i2bcam = R_sc2inertial.dot(R_sc2bcam.T)
    R_blender = R_sc2inertial.dot(R_sc2bcam.T)
    # rot_euler = mathutils.Matrix(R_i2bcam).to_euler('XYZ')
    # rot_euler = mathutils.Matrix(R_sc2inertial.dot(R_sc2bcam.T)).to_euler('XYZ')
    rot_euler = mathutils.Matrix((R_sc2inertial.dot(R_sc2bcam.T))).to_euler('XYZ')

    camera_obj.rotation_euler = rot_euler
    bpy.context.scene.update()

    RT = blender_camera.get_3x4_RT_matrix_from_blender(camera_obj)
    # render an image from the spacecraft at this state
    # blender_render(filename,scene, True)
    scene.render.filepath = os.path.join(output_path + '/' + filename + '.png')
    bpy.ops.render.render(write_still=True)
    img = cv2.imread(os.path.join(output_path + '/' + filename + '.png')) # read as color BGR in OpenCV

    return img, np.array(RT), R_blender


def gen_image_fixed_ast(sc_pos, R_sc2inertial, camera_obj, camera, 
                        lamp_obj, lamp, itokawa_obj, scene, 
                        sun_position=[-5, 0, 1], filename='test'):
    r"""This will generate a blender render given a camera position and
    orientation

    Generate a single image given a known position and orientation of the
    camera/spacecraft. The image is returned as an output.

    Parameters
    ----------
    sc_pos : (3,) array_like and float Position of the spacecraft/camera in the
    inertial frame (blender world coordinates) The units are in kilometers (1
    Blender unit is 1 km)
    R_sc2ast : (3, 3) numpy array of float
        Rotation matrix which transforms vectors in teh spacecraft body frame
        to the inertial frame.
        The camera is rotated to be assumed to point along the body frame +X axis
    theta_ast : float
        Angle of rotation about z axis of the asteroid at current time
    filename : string
        Name of PNG file to save the rendered image

    Returns
    -------
    img : np.array_
        Blender saves an image then OpenCV reads it and passes it back,
        same image is overwritten the next step



    Notes
    -----
    To transform vectors from the camera frame to the inertial/world frame

    .. math:: R_{I2B} = R_{S2I} * R_{B2S} 

    Rotation operations in blender are from the object/body frame to the
    inertial frame.  Therefore, in order to rotate an object with respect to
    the inertial frame you'll need to use the transpose.  Blender uses the same
    standard as most of the dynamics/papers, except for visualization we want
    the opposite.

    Author
    ------
    Shankar Kulumani		GWU		skulumani@gwu.edu

    References
    ----------
    This relies on the Blender Python Module.

    .. [1] https://wiki.blender.org/index.php/User:Ideasman42/BlenderAsPyModule 
    .. [2] Look at utilities/build_blender.sh for automatic building 


    """  
    
    # move camera and asteroid 
    camera_obj.location = sc_pos
    lamp_obj.location = sun_position
    
    # rotate asteroid
    itokawa_obj.location = [0, 0, 0]
    itokawa_obj.rotation_euler = mathutils.Euler((0, 0, 0), 'XYZ')

    # rotate the camera
    R_i2bcam = R_sc2inertial.dot(R_sc2bcam.T)
    R_blender = R_sc2inertial.dot(R_sc2bcam.T)
    # rot_euler = mathutils.Matrix(R_i2bcam).to_euler('XYZ')
    # rot_euler = mathutils.Matrix(R_sc2inertial.dot(R_sc2bcam.T)).to_euler('XYZ')
    rot_euler = mathutils.Matrix((R_sc2inertial.dot(R_sc2bcam.T))).to_euler('XYZ')

    camera_obj.rotation_euler = rot_euler
    bpy.context.scene.update()

    RT = blender_camera.get_3x4_RT_matrix_from_blender(camera_obj)
    # render an image from the spacecraft at this state
    # blender_render(filename,scene, True)
    scene.render.filepath = os.path.join(output_path + '/' + filename + '.png')
    bpy.ops.render.render(write_still=True)
    img = cv2.imread(os.path.join(output_path + '/' + filename + '.png')) # read as color BGR in OpenCV

    return img, np.array(RT), R_blender

def write_h5py_to_png(hdf5_path, dataset_name, output_path):
    """Write a series of images to PNGs from HDF5 file
    
    The simulation will save all the image data into a HDF5 file. 
    This function will read the dataset and save each one to a different image

    Parameters :
    ------------
    hdf5_path : string
        Path to the HDF5 file to read
    dataset_name : string
        Name of the images in the HDF5 file
    output_path : string
        Where to save all the images

    Returns :
    ---------
    None

    """
    sim_data = h5py.File(hdf5_path, 'r')

    images = sim_data[dataset_name]

    num_images = images.shape[3]

    for ii in range(num_images):
        cv2.imwrite(output_path + '/test' + str.zfill(str(ii), 6) + '.png', images[:, :, :, ii])
        print("Saving image {0}/{1}".format(ii, num_images))

    print("Finished extracting all the images")

    return 0
