import lattice as lt
from lattice_renderer import LatticeRenderer
import sys, cProfile

def main():
  if len(sys.argv) != 4:
    sys.exit("Please supply two arguments: the path to the exported mesh nodes and the path to the exported stresses.")

  stress_mesh = lt.StressMesh(sys.argv[1],sys.argv[2])
  lattice = lt.Lattice(stress_mesh, int(sys.argv[3]), 1)
  lr = LatticeRenderer()
  lr.load_lattice(lattice, extrude_width = 0.5)
  lr.render()

if __name__ == '__main__': 
  main()
  #cProfile.run('main()')