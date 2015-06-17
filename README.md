# LatticeUtility
A utility to generate, visualize, and make toolpaths for 3D printable stress-optimized lattices

## Aims

- [x] Import finite element analysis results in the form of a mesh of normal stresses.
- [x] Generate a lattice data structure from a stress mesh with adjustable cube unit widths.
- [x] Vary internal edges in the lattice according to stress magnitude.
- [x] Render an interactive lattice visualization of the lattice
- [ ] Generate toolpaths for 3D printing the lattice with a robot arm
- [ ] Make the toolpaths exportable to the Rhino/Grasshopper HAL system

## Dependencies
1. numpy
2. scipy
3. vispy
4. PyQt or similar
