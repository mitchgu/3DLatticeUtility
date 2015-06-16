import lattice as lt
from lattice_renderer import LatticeRenderer
import sys, cProfile

def main():
  if len(sys.argv) != 3:
    sys.exit("Please supply two arguments: the path to the exported mesh nodes and the path to the exported stresses.")
  node_file_path = sys.argv[1]
  stress_file_path = sys.argv[2]
  cunit_size = float(raw_input("Enter cube unit size (mm) [Default 10mm]: ") or 10)
  mesh_size = float(raw_input("Enter resolution of mesh (mm) [Default is cube unit size]: ") or cunit_size)
  stress_scale = float(raw_input("Enter stress magnitude scale [Default 1]: ") or 1)
  extrude_width = float(raw_input("Enter filament extrusion width [Default 1mm]: ") or 1.0)

  print "Creating a stress mesh from FEA files"
  stress_mesh = lt.StressMesh(node_file_path,stress_file_path, mesh_size)
  print "Generating a lattice from stress mesh and parameters given"
  lattice = lt.Lattice(stress_mesh, cunit_size, stress_scale)
  print "Setting up the visualization window"
  lr = LatticeRenderer()
  print "Loading the lattice into the visualization"
  lr.load_better_lattice(lattice, extrude_width)
  print "Running visualization"
  lr.render()

if __name__ == '__main__': 
  main()
  #cProfile.run('main()')