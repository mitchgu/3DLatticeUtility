import numpy as np
import csv

class Toolpath:
  # Toolpath format:
  # [point to move to, time to reach point, extruder orientation vector, extrude rate]

  I,J,K = np.array([1,0,0]),np.array([0,1,0]),np.array([0,0,1])
  SPEED = 20 # mm/s
  ORIENTATION = (0,0,-1) # -k direction
  ERATE = 1
  LAYER0_ORDER = [I, I + J, J, np.zeros(3)]

  def __init__(self, lattice):
    self.lattice = lattice
    self.toolpath = []
    self.vertices = []
    self.extruded = set()
    layer0 = lattice.cunits[:,:,0]
    dim = lattice.dim
    previous_point = (0,0,0)
    for i in xrange(dim[0]):
      for j in xrange(dim[1]):
        cu = layer0[i,j]
        if cu is not None and cu.sz is not None:
          vertex = np.array(cu.vertex) * lattice.cs
          self.toolpath.append([tuple(vertex), 1, self.ORIENTATION, 0])
          self.vertices.append(tuple(vertex))
          for k in xrange(4):
            target = tuple(vertex + self.LAYER0_ORDER[k] * lattice.cs)
            if (previous_point, target) not in self.extruded and (target, previous_point) not in self.extruded:
              self.toolpath.append([target, 1, self.ORIENTATION, self.ERATE])
              self.vertices.append(target)
              previous_point = target
              self.extruded.add((previous_point, target))
    self.export_toolpath()

  def export_toolpath(self):
    with open('toolpath.txt', 'wb') as myfile:
      wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
      for instruction in self.toolpath:
        wr.writerow(instruction)