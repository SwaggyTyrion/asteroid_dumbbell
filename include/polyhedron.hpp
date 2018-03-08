#ifndef BUILD_POLY_H
#define BUILD_POLY_H

#include <CGAL/Simple_cartesian.h>
#include <CGAL/Polyhedron_3.h>
#include <CGAL/Polyhedron_items_with_id_3.h>

#include <Eigen/Dense>

// Create a class that contains all the data of interest
// Should hold P
// Should hold Eigen V and F of P
// Have access methods to take V/F and update P
// Return V, F method
// Polyhedron potential method which takes a state and returns the gravity, accel etc
class Poly {
    public:
        Poly();
        Poly(const Eigen::MatrixXd &V_input, const Eigen::MatrixXi &F_input);
        Poly(const std::string input_file);

        Eigen::MatrixXd get_vertices();
        Eigen::MatrixXi get_faces();
        void build_poly();

        CGAL::Polyhedron_3<CGAL::Simple_cartesian<double>, CGAL::Polyhedron_items_with_id_3> get_polyhedron();

    private:
        CGAL::Polyhedron_3<CGAL::Simple_cartesian<double>, CGAL::Polyhedron_items_with_id_3 > P;
        Eigen::MatrixXd V;
        Eigen::MatrixXi F;
};

// TODO This declaration should remain private. Move ot only CPP file
// declaration for the polyhedron builder
template<typename HDS> 
class Polyhedron_builder : public CGAL::Modifier_base<HDS> {
    public:
        // TODO Think about making a giant class that holds P, V, F, and anything else important
        Eigen::MatrixXd V;
        Eigen::MatrixXi F;

        Polyhedron_builder(Eigen::MatrixXd &V_input, Eigen::MatrixXi &F_input) : V(V_input), F(F_input) {}
    
        void operator() (HDS &hds);		
};

template<typename VectorType, typename IndexType>
void polyhedron_to_eigen(CGAL::Polyhedron_3<CGAL::Simple_cartesian<double>, CGAL::Polyhedron_items_with_id_3 > &P,
        Eigen::PlainObjectBase<VectorType> &V, Eigen::PlainObjectBase<IndexType> &F);


void eigen_to_polyhedron(Eigen::MatrixXd &V,Eigen::MatrixXi &F,
        CGAL::Polyhedron_3<CGAL::Simple_cartesian<double>, CGAL::Polyhedron_items_with_id_3 > &P);

// TODO This should be private as well. Only in CPP
void build_polyhedron_index(CGAL::Polyhedron_3<CGAL::Simple_cartesian<double>, CGAL::Polyhedron_items_with_id_3> &P);

void print_polyhedron_stats(CGAL::Polyhedron_3<CGAL::Simple_cartesian<double>, CGAL::Polyhedron_items_with_id_3> &P);

#endif
