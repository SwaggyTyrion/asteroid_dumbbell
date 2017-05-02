
import numpy as np

import kinematics.attitude as attitude

def inertial2ast(time, state, ast, dum):
    """Convert inertial state to the asteroid fixed frame
    
    This will convert a state vector which is defined in the inertial frame
    into the equivalent representation in the rotating asteroid frame. 

    Inputs:
        time - nx1 array of time stamps for the state vector
        state - nx18 array of the state vector defined as follows:
            inertial_pos - state[:, 0:3] is the position of the body with respect to the asteroid 
                center and defined in the inertial frame
            inertial_vel - state[:, 4:6] is the velocity of the sc with respect to the asteroid 
                center of mass and defined in the inertial frame
            R_sc2int - state[:, 6:15] the rotation matrix which transforms vectors from the sc frame
                to the inertial frame
            inertial_w - state[:, 15:18] the angular velocity of the sc with respect to the inertial
                frame and defined in the inertial frame
        ast - Instance of Asteroid class
        dum - Instance of Dumbbell class

    Outputs:
        ast_state - the state as represented in the rotating asteroid fixed frame
            ast_pos - ast_state[:, 0:3] is the position of the sc with respect to the asteroid
                fixed frame and represented in the asteroid frame
            ast_vel - ast_state[:, 3:6] is the velocity of the sc with respect to the asteroid and 
                represented in the asteroid fixed frame
            ast_R_sc2ast - ast_state[:, 6:15] is the transformation from the sc frame to the asteroid
                frame
            ast_w - ast_state[:, 15:18] is the angular velocity of the sc with respect ot the inertial 
                frame and defined in the asteroid rotating frame

    """

    # figure out transformation from inertial frame to relative frame
    Rast2int = np.zeros((3,3,time.shape[0]))
    Rint2ast = np.zeros((3,3,time.shape[0]))

    ast_state = np.zeros(state.shape)

    for ii,t in np.ndenumerate(time):
        Rast2int[:,:,ii] = attitude.rot3(ast.omega*t, 'c')[:,:,np.newaxis] # asteroid body frame to inertial frame
        Rint2ast[:,:,ii] = attitude.rot3(ast.omega*t, 'c').T[:,:,np.newaxis]

        Ra = np.squeeze(Rast2int[:,:,ii])
        # convert inertial states to relative states
        inertial_pos = np.squeeze(state[ii,0:3])
        inertial_vel = np.squeeze(state[ii,3:6])
        R_sc2int = np.squeeze(state[ii,6:15].reshape(3,3))
        inertial_w = np.squeeze(state[ii,15:18])

        ast_pos = Ra.T.dot(inertial_pos)
        ast_vel = Ra.T.dot(inertial_vel)
        ast_R_sc2ast = Ra.T.dot(R_sc2int).reshape(9)
        ast_w = ast_R_sc2ast.reshape((3,3)).dot(inertial_w)

        ast_state[ii,:] = np.hstack((ast_pos, ast_vel, ast_R_sc2ast, ast_w))

    return ast_state,Rast2int, Rint2ast

def ast2inertial(time, state, ast, dum):
    """Convert from the asteroid frame to the inertial frame
     
    This will convert a state vector which is defined in the asteroid frame
    into the equivalent representation in the inertial frame. 

    Inputs:
        time - nx1 array of time stamps for the state vector
        state - nx18 array of the state vector defined as follows:
            ast_pos - state[:, 0:3] is the position of the body with respect to the asteroid 
                center and defined in the asteroid frame
            ast_vel - state[:, 4:6] is the velocity of the sc with respect to the asteroid 
                center of mass and defined in the asteroid frame
            R_sc2ast - state[:, 6:15] the rotation matrix which transforms vectors from the sc frame
                to the asteroid frame
            ast_w - state[:, 15:18] the angular velocity of the sc with respect to the inertial
                frame and defined in the asteroid frame
        ast - Instance of Asteroid class
        dum - Instance of Dumbbell class

    Outputs:
        inertial_state - the state as represented in the rotating asteroid fixed frame
            inertial_pos - inertial_state[:, 0:3] is the position of the sc with respect to the asteroid
                fixed frame and represented in the inertial frame
            inertial_vel - inertial_state[:, 3:6] is the velocity of the sc with respect to the asteroid and 
                represented in the inertial fixed frame
            inertial_R_sc2int - inertial_state[:, 6:15] is the transformation from the sc frame to the inertial
                frame
            inertial_w - inertial_state[:, 15:18] is the angular velocity of the sc with respect to the inertial 
                frame and defined in the inertial frame


    """

    # transformation between asteroid fixed frame and inertial frame
    # figure out transformation from inertial frame to relative frame
    Rast2int = np.zeros((3, 3, time.shape[0]))
    Rint2ast = np.zeros((3, 3, time.shape[0]))

    inertial_state = np.zeros(state.shape)

    for ii, t in np.ndenumerate(time):
        Rast2int[:, :, ii] = attitude.rot3(ast.omega*t, 'c')[:, :, np.newaxis] # asteroid body frame to inertial frame
        Rint2ast[:, :, ii] = attitude.rot3(ast.omega*t, 'c').T[:, :, np.newaxis]

        Ra = np.squeeze(Rast2int[:, :, ii])
        # convert the relative state to the inertial frame
        ast_pos = np.squeeze(state[ii, 0:3])
        ast_vel = np.squeeze(state[ii, 3:6])
        R_sc2ast = np.squeeze(state[ii, 6:15].reshape(3, 3))
        ast_w = np.squeeze(state[ii, 15:18])

        inertial_pos = Ra.dot(ast_pos)
        inertial_vel = Ra.dot(ast_vel)
        inertial_R_sc2int = Ra.dot(R_sc2ast).reshape(9)
        inertial_w = Ra.dot(ast_w)

        inertial_state[ii, :] = np.hstack((inertial_pos, inertial_vel, inertial_R_sc2int, inertial_w))

    return inertial_state, Rast2int, Rint2ast

def body2inertial(time, state, ast, dum):
    """Convert SC state to inertial state
 
    This will convert a state vector which is defined in the spacecraft frame
    into the equivalent representation in the inertial frame. 

    Inputs:
        time - nx1 array of time stamps for the state vector
        state - nx18 array of the state vector defined as follows:
            inertial_pos - state[:, 0:3] is the position of the body with respect to the asteroid 
                center and defined in the inertial frame
            inertial_vel - state[:, 4:6] is the velocity of the sc with respect to the asteroid 
                center of mass and defined in the inertial frame
            R_sc2int - state[:, 6:15] the rotation matrix which transforms vectors from the sc frame
                to the inertial frame
            body_w - state[:, 15:18] the angular velocity of the sc with respect to the inertial
                frame and defined in the spacecraft frame
        ast - Instance of Asteroid class
        dum - Instance of Dumbbell class

    Outputs:
        inertial_state - the state as represented in the rotating inertial frame
            inertial_pos - inertial_state[:, 0:3] is the position of the sc with respect to the asteroid
                fixed frame and represented in the inertial frame
            inertial_vel - inertial_state[:, 3:6] is the velocity of the sc with respect to the asteroid and 
                represented in the inertial fixed frame
            inertial_R_sc2int - inertial_state[:, 6:15] is the transformation from the sc frame to the inertial
                frame
            inertial_w - inertial_state[:, 15:18] is the angular velocity of the sc with respect to the inertial 
                frame and defined in the inertial frame


    """
    inertial_state = np.zeros(state.shape)

    for ii, t in np.ndenumerate(time):

        # convert the relative state to the inertial frame
        inertial_pos = np.squeeze(state[ii, 0:3])
        inertial_vel = np.squeeze(state[ii, 3:6])
        R_sc2int = np.squeeze(state[ii, 6:15])
        body_w = np.squeeze(state[ii, 15:18])

        inertial_w = R_sc2int.reshape((3, 3)).dot(body_w)

        inertial_state[ii, :] = np.hstack((inertial_pos, inertial_vel,R_sc2int, inertial_w))

    return inertial_state 

def body2ast(time, state, ast, dum):
    """Convert state from the body frame to the asteroid fixed frame

    This function will convert the state output of eoms_inertial to the asteroid fixed frame.
    This wil allow for comparision with the state from eoms_relative.

    Inputs:
        time - nx1 array of time stamps for the state vector
        state - nx18 array of the state vector defined as follows:
            inertial_pos - state[:, 0:3] is the position of the body with respect to the asteroid 
                center and defined in the inertial frame
            inertial_vel - state[:, 4:6] is the velocity of the sc with respect to the asteroid 
                center of mass and defined in the inertial frame
            R_sc2int - state[:, 6:15] the rotation matrix which transforms vectors from the sc frame
                to the inertial frame
            body_w - state[:, 15:18] the angular velocity of the sc with respect to the inertial
                frame and defined in the spacecraft frame
        ast - Instance of Asteroid class
        dum - Instance of Dumbbell class

    Outputs:
        ast_state - the state as represented in the rotating asteroid frame
            ast_pos - ast_state[:, 0:3] is the position of the sc with respect to the asteroid
                fixed frame and represented in the asteroid frame
            ast_vel - ast_state[:, 3:6] is the velocity of the sc with respect to the asteroid and 
                represented in the asteroid fixed frame
            ast_R_sc2ast - ast_state[:, 6:15] is the transformation from the sc frame to the asteroid
                frame
            ast_w - ast_state[:, 15:18] is the angular velocity of the sc with respect to the inertial 
                frame and defined in the asteroid frame
    """
    # transformation between asteroid fixed frame and inertial frame
    # figure out transformation from inertial frame to relative frame
    Rast2int = np.zeros((3, 3, time.shape[0]))
    Rint2ast = np.zeros((3, 3, time.shape[0]))

    ast_state = np.zeros(state.shape)

    for ii, t in np.ndenumerate(time):
        Rast2int[:, :, ii] = attitude.rot3(ast.omega*t, 'c')[:, :, np.newaxis] # asteroid body frame to inertial frame
        Rint2ast[:, :, ii] = attitude.rot3(ast.omega*t, 'c').T[:, :, np.newaxis]

        Ra = np.squeeze(Rast2int[:, :, ii])
        # convert the relative state to the inertial frame
        body_pos = np.squeeze(state[ii, 0:3])
        body_vel = np.squeeze(state[ii, 3:6])
        R_sc2int = np.squeeze(state[ii, 6:15].reshape(3, 3))
        body_w = np.squeeze(state[ii, 15:18])

        ast_pos = Ra.T.dot(body_pos)
        ast_vel = Ra.T.dot(body_vel)
        ast_R_sc2ast = Ra.T.dot(R_sc2int).reshape(9)
        ast_w = ast_R_sc2ast.reshape((3, 3)).dot(body_w)

        ast_state[ii, :] = np.hstack((ast_pos, ast_vel, ast_R_sc2ast, ast_w))

    return ast_states

