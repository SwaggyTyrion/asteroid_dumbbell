#include "loader.hpp"
#include "mesh.hpp"
#include "reconstruct.hpp"
#include "geodesic.hpp"
#include "surface_mesher.hpp"
#include "cgal.hpp"
#include "polyhedron.hpp"
#include "lidar.hpp"
#include "controller.hpp"
#include "state.hpp"

#include "input_parser.hpp"

#include <memory>
#include <iostream>

int main(int argc, char* argv[])
{
    // CONSTANTS
    // semi major axes of castalia
    Eigen::Vector3d axes(3);
    axes << 1.6130 / 2.0, 0.9810 / 2.0, 0.8260 / 2.0;
    double min_angle(10), max_radius(0.03), max_distance(0.5);

    InputParser input(argc, argv);
    if (input.option_exists("-h")) {
        std::cout << "Kinematic only exploration with asteroid reconstruction" << std::endl;

    }
    const std::string input_file = input.get_command_option("-i");
    if (input_file.empty()) {
        std::cout << "You need to input file name!" << std::endl;
        std::cout << "explore -i asteroid.obj" << std::endl;
        return 1;
    }

    // initialize all the objects
    std::shared_ptr<MeshData> true_asteroid;
    true_asteroid = Loader::load(input_file);
     
    RayCaster caster(true_asteroid);
    SurfMesh ellipsoid(axes(0), axes(1), axes(2),
            min_angle, max_radius, max_distance);
    ReconstructMesh rmesh(ellipsoid.verts(), ellipsoid.faces());
    Controller controller;

    Lidar sensor;
    double dist = 5;
    int num_steps = 3;
    sensor.dist(dist).num_steps(num_steps);

    // place satellite in a specific location and define view axis
    State initial_state, state;
    initial_state.pos((Eigen::RowVector3d() << 1.5, 0, 0).finished())
         .vel((Eigen::RowVector3d() << 0, 0, 0).finished())
         .att((Eigen::MatrixXd::Identity(3, 3)))
         .ang_vel((Eigen::RowVector3d() << 0, 0, 0).finished());
    std::shared_ptr<State> state_ptr = std::make_shared<State>(state);
    std::shared_ptr<State> initial_state_ptr = std::make_shared<State>(initial_state);

    state_ptr->update_state(initial_state_ptr);
    // modify the initial state to point at the body using the controller
    // targets to be updated in the loop
    Eigen::Matrix<double, 1, 3> target(1, 3);
    Eigen::Matrix<double, 1, 3> intersection(1, 3);

    // LOOP HERE
    for (int ii = 0; ii < 1; ++ii) {
        
        // compute targets for use in caster (point at the asteroid origin)
        target = sensor.define_target(state_ptr->get_pos(), state_ptr->get_att(), dist);    

        // perform raycasting on the true mesh (true_asteroid pointer)
        intersection = caster.castray(state_ptr->get_pos(), target);

        // use this measurement to update rmesh (inside holds teh mesh estimate)
        // use the updated weight to find a new positoin to move to
        // update the state ptr with the newly calculated state
        // save the data (raycast interseciton, position of sat, ast estimate, targets) to hdf5
        // LOOP
    }
    std::cout << target << std::endl;
    std::cout << intersection << std::endl;
    
    AttitudeController att_control;
    /* att_control.body_fixed_pointing_attitude(0.0, state); */
    return 0;
}
