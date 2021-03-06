// Tell swig the name of the module we're creating
%module pymass

// Pull in the headers from Python itself and from our library
%{
#define SWIG_FILE_WITH_INIT
#define SWIG_PYTHON_STRICT_BYTE_CHAR
#include <Python.h>
#include "pymass_export.h"
#include "LCMS.h"
#include "mzXMLParser.h"
#include "utils.h"
%}

%include <typemaps.i>
%include <std_string.i>
%include <std_vector.i>


namespace std {
   %template(BoolVector) vector<bool>;
   %template(IntVector) vector<int>;
   %template(DoubleVector) vector<double>;
   %template(StringVector) vector<string>;
   %template(ConstCharVector) vector<const char*>;
   %template(MassScanVector) vector<MassScan>;
   %template(VV3f) vector<Eigen::Vector3f>;
   %template(VV4f) vector<Eigen::Vector4f>;
   %template(PICVec) vector<Eigen::MatrixXf>;
}


// Eigen matrices into Numpy arrays.
%include <eigen.i>
%eigen_typemaps(Eigen::VectorXd)
%eigen_typemaps(Eigen::MatrixXd)
%eigen_typemaps(Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic>)
%eigen_typemaps(Eigen::Vector3f)
%eigen_typemaps(Eigen::Vector4f)
%eigen_typemaps(Eigen::VectorXf)
%eigen_typemaps(Eigen::MatrixXf)
%eigen_typemaps(Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic>)
%eigen_typemaps(Eigen::VectorXi)
%eigen_typemaps(Eigen::Matrix<int, Eigen::Dynamic, 1>)



// Tell swig to build bindings for everything in our library
%include <windows.i>
%include "pymass_export.h"
%include "LCMS.h"
%include "mzXMLParser.h"
%include "utils.h"

