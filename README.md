# LatticeUtility
A utility to generate, visualize, and make toolpaths for 3D printable stress-optimized lattices

## Aims
1. Import finite element analysis results in the form of a mesh of normal stresses. (done)
2. Generate a lattice data structure from a stress mesh with adjustable cube unit widths. (done)
3. Vary internal edges in the lattice according to stress magnitude. (in progress)
4. Render an interactive lattice visualization of the lattice (in progress)
5. Generate toolpaths for 3D printing the lattice with a robot arm (a ways away)

## Dependencies
1. numpy
2. scipy
3. vispy
4. PyQt or similar
