import numpy as np
from scipy import spatial
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt

class StressMesh:
  def __init__(self, node_file, stress_file):
    self.nodes = np.genfromtxt(
      node_file,
      dtype = 'f4',
      delimiter = ',',
      skip_header = 8,
      usecols = (2,3,4),
      autostrip = True
      )
    self.stresses = np.genfromtxt(
      stress_file,
      dtype = 'f4',
      delimiter = ',',
      skip_header = 5,
      usecols = (1,2,3),
      autostrip = True
      )
    self.min_p = np.amin(self.nodes, axis=0)
    self.max_p = np.amax(self.nodes, axis=0)
    self.bounds = self.max_p - self.min_p
    self.max_stress = abs(max(np.amax(self.stresses), np.amin(self.stresses), key=abs))
    self.node_tree = spatial.KDTree(self.nodes)

  def nearest_stress(self, point, dist=float('inf'), absV=True, norm=True):
    nearest_node = self.node_tree.query(point, distance_upper_bound = dist)
    if nearest_node[0] == float('inf'):
      return None
    stress = self.stresses[nearest_node[1]]
    if norm: stress = stress / self.max_stress
    return np.absolute(stress) if absV else stress

class Cunit:
  I,J,K = np.array([1,0,0]),np.array([0,1,0]),np.array([0,0,1])

  def __init__(self, vertex, stress, parent):
    self.vertex = vertex
    self.sx = stress[0]
    self.sy = stress[1]
    self.sz = stress[2]
    self.xpe = np.array([self.vertex, self.vertex + self.I])
    self.ype = np.array([self.vertex, self.vertex + self.J])
    self.zpe = np.array([self.vertex, self.vertex + self.K])
    self.parent = parent
    self._empty_neighbors = None

  def __str__(self):
    return str(self.stress)

  @property
  def vertices(self):
    vertices = set([tuple(self.vertex)])
    if self.sx is not None:
      for offset in [self.J, self.K, self.J + self.K]:
        vertices.add(tuple(self.vertex + offset))
    if self.sy is not None:
      for offset in [self.I, self.K, self.I + self.K]:
        vertices.add(tuple(self.vertex + offset))
    if self.sz is not None:
      for offset in [self.I, self.J, self.I + self.J]:
        vertices.add(tuple(self.vertex + offset))
    return vertices

  @property
  def principal_edges(self):
    principal_edges = set()
    toTuple = lambda a: tuple(map(tuple,a))
    if self.sx is not None:
      for edge in [self.ype,self.ype+self.K,self.zpe,self.zpe+self.J]:
        principal_edges.add(toTuple(edge))
    if self.sy is not None:
      for edge in [self.xpe,self.xpe+self.K,self.zpe,self.zpe+self.I]:
        principal_edges.add(toTuple(edge))
    if self.sz is not None:
      for edge in [self.xpe,self.xpe+self.J,self.ype,self.ype+self.I]:
        principal_edges.add(toTuple(edge))
    return principal_edges

class Lattice:
  def __init__(self, stress_mesh, cunit_width, scale = 1):
    self.stress_mesh = stress_mesh
    self.generate_cunits(cunit_width, scale)

  def generate_cunits(self, cunit_width, scale = 1):
    self.cunit_width = cunit_width
    self.dim = np.ceil(self.stress_mesh.bounds / cunit_width).astype(int) + np.ones(3, dtype=int)
    self.lattice_points = set()
    self.cunits = np.empty(self.dim, dtype = object)
    dp = np.array([0, cunit_width / 2., cunit_width / 2.])
    near_radius = cunit_width * 0.49
    for i in xrange(self.dim[0]):
      for j in xrange(self.dim[1]):
        for k in xrange(self.dim[2]):
          point = np.array([i,j,k]) * cunit_width + self.stress_mesh.min_p
          stress = [None] * 3
          void = 0
          for a in xrange(3):
            stress[a] = self.stress_mesh.nearest_stress(point+np.roll(dp,a), dist = near_radius)
            if stress[a] is None:
              void += 1
            else: 
              stress[a] = np.delete(stress[a],a)
              if scale != 1: stress[a] = [np.minimum(stress[a] * scale, np.ones(2))]
          if void == 3:
            continue
          else:
            self.lattice_points.add((i,j,k))
            self.cunits[i,j,k] = Cunit(np.array([i,j,k]), stress, self) 
      