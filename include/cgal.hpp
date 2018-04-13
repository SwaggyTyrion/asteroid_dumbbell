#ifndef CGAL_H
#define CGAL_H

#include "cgal_types.hpp"
#include "mesh.hpp"

#include <Eigen/Dense>

#include <memory>
#include <cmath>

// Use the dD spatial searching package for finding nearest vertices/primitives
class MeshDistance {
    public:
        MeshDistance(std::shared_ptr<MeshData> mesh_in);
        
        void update_mesh(std::shared_ptr<MeshData> mesh_in);
        // funciton to compute distance from pt to mesh and return minimum distance, and primitive
        int k_nearest_neighbor(const Eigen::Ref<const Eigen::Vector3d>& pt, const int &K);

    private:
        std::shared_ptr<MeshData> mesh;
        Vertex_point_pmap vppmap;
};

class RayCaster {
    public:
        RayCaster(std::shared_ptr<MeshData> mesh_in);

        // cast ray function
        Eigen::Matrix<double, 1, 3> castray(const Eigen::Ref<const Eigen::Vector3d>& psource,
                const Eigen::Ref<const Eigen::Vector3d>& ptarget);

        // cast many rays function
        Eigen::Matrix<double, Eigen::Dynamic, 3> castarray(const Eigen::Ref<const Eigen::Vector3d> &psource,
                                                           const Eigen::Ref<const Eigen::Matrix<double, Eigen::Dynamic, 3> > &targets);

        // update the raycaster with a new mesh ptr
        void update_mesh(std::shared_ptr<MeshData> mesh_in);

        /**
            Compute the minimum distance to the mesh

            This uses the AABB tree to find the distance from a point to the 
            polyhedron.

            @param pt Eigen::Vector3d point defining the test point
            @returns Double distance type
        */
        double minimum_distance(const Eigen::Ref<const Eigen::Vector3d> &pt);

        void minimum_primitive(const Eigen::Ref<const Eigen::Vector3d> &pt);
    private:
        // needs the mesh to operate on
        std::shared_ptr<MeshData> mesh;
        AABB_Tree tree; // holds the AABB tree for CGAL distance computations
};

#endif
