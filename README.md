# LDH_MBT_codes
Python codes used in LDH_MBT article

Python code to calculate the angles from the planes and/or lines of atoms from the Molecular Dynamics (MD) done with Gromacs package.
The code extract the geometries from a trajectory file (.trr) to .gro files of each frame of MD simulation. Filter the XYZ information of each atom, calculate the distances of neighbour and calculate the vector of plane or line taht describe the selected atom. The angle of tese vectors is saved in angles.dat and the histogram of angles in histogram.dat.
To accelerate the process of angle calculation is used a multiprocessing process. 
