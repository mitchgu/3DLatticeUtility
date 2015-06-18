import lattice as lt
from lattice_renderer import LatticeRenderer
from toolpathing import Toolpath
import sys, cProfile, math

def main():
  if len(sys.argv) != 3:
    sys.exit("Please supply two arguments: the path to the exported mesh nodes and the path to the exported stresses.")
  node_file_path = sys.argv[1]
  stress_file_path = sys.argv[2]
  cunit_size = float(raw_input("Enter cube unit size (mm) [Default 10mm]: ") or 10)
  mesh_size = float(raw_input("Enter resolution of mesh (mm) [Default is cube unit size]: ") or cunit_size)
  stress_scale = float(raw_input("Enter stress magnitude scale [Default 1]: ") or 1)
  extrude_width = float(raw_input("Enter filament extrusion width [Default 1mm]: ") or 1.0)
  render_method = raw_input("Use dynamic lattice loading? (slower) [Y or N] [Default N]: ") or 'N'
  render_dynamic_lattice = True if render_method == 'Y' or render_method == 'y' else False
  generate_toolpath = raw_input("Generate toolpath? [Y or N] [Default N]: ") or 'N'
  generate_toolpath = True if generate_toolpath == 'Y' or generate_toolpath == 'y' else False


  max_n = int(math.floor(cunit_size / extrude_width) - 1)

  print "Creating a stress mesh from FEA files"
  stress_mesh = lt.StressMesh(node_file_path,stress_file_path, mesh_size)
  print "Generating a lattice from stress mesh and parameters given"
  lattice = lt.Lattice(stress_mesh, cunit_size, max_n, stress_scale)
  if generate_toolpath: 
    print "Generating toolpath"
    toolpath = Toolpath(lattice)
  print "Setting up the visualization window"
  lr = LatticeRenderer()
  if generate_toolpath:
    print "Loading the toolpath into the visualization"
    lr.load_toolpath(toolpath)
  print "Loading the lattice into the visualization"
  if render_dynamic_lattice:
    lr.load_dynamic_lattice(lattice)
  else: 
    lr.load_lattice(lattice)
  print "Running visualization"
  lr.render()

if __name__ == '__main__': 
  main()
  #cProfile.run('main()')