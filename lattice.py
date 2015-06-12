import numpy as np
from scipy import spatial

class StressMesh:
  def __init__(self, node_file, stress_file, mesh_size):
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
    self.mesh_size = mesh_size
    self.min_p = np.amin(self.nodes, axis=0)
    self.max_p = np.amax(self.nodes, axis=0)
    self.bounds = self.max_p - self.min_p
    print "Part Dimensions: " + " x ".join(list(self.bounds.astype(str)))
    self.max_stress = abs(max(np.amax(self.stresses), np.amin(self.stresses), key=abs))
    print "Maximum Stress: " + str(self.max_stress)
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
  _vertices = None
  _principal_edges = None
  _inner_edges = None

  def __init__(self, vertex, stress, parent):
    self.vertex = vertex
    self.sx = stress[0]
    self.sy = stress[1]
    self.sz = stress[2]
    self.xpe = np.array([self.vertex, self.vertex + self.I])
    self.ype = np.array([self.vertex, self.vertex + self.J])
    self.zpe = np.array([self.vertex, self.vertex + self.K])
    self.parent = parent

  def __str__(self):
    return str(self.stress)

  @property
  def vertices(self):
    if self._vertices is None:
      self._vertices = set([tuple(self.vertex)])
      if self.sx is not None:
        for offset in [self.J, self.K, self.J + self.K]:
          self._vertices.add(tuple(self.vertex + offset))
      if self.sy is not None:
        for offset in [self.I, self.K, self.I + self.K]:
          self._vertices.add(tuple(self.vertex + offset))
      if self.sz is not None:
        for offset in [self.I, self.J, self.I + self.J]:
          self._vertices.add(tuple(self.vertex + offset))
    return self._vertices

  @property
  def principal_edges(self):
    if self._principal_edges is None:
      self._principal_edges = set()
      toTuple = lambda a: tuple(map(tuple,a))
      if self.sx is not None:
        for edge in [self.ype,self.ype+self.K,self.zpe,self.zpe+self.J]:
          self._principal_edges.add(toTuple(edge))
      if self.sy is not None:
        for edge in [self.xpe,self.xpe+self.K,self.zpe,self.zpe+self.I]:
          self._principal_edges.add(toTuple(edge))
      if self.sz is not None:
        for edge in [self.xpe,self.xpe+self.J,self.ype,self.ype+self.I]:
          self._principal_edges.add(toTuple(edge))
    return self._principal_edges

  def inner_edges(self, max_n):
    if self._inner_edges is None:
      self._inner_edges = []
      if self.sx is not None: 
        num1,num2 = tuple(np.rint(self.sx * max_n).astype(int))
        step1,step2 = 1.0/(num1+1), 1.0/(num2+1)
        self._inner_edges += [self.ype + i*step1*self.K for i in xrange(1,num1+1)]
        self._inner_edges += [self.zpe + i*step2*self.J for i in xrange(1,num2+1)]
      if self.sy is not None: 
        num1,num2 = tuple(np.rint(self.sy * max_n).astype(int))
        step1,step2 = 1.0/(num1+1), 1.0/(num2+1)
        self._inner_edges += [self.xpe + i*step1*self.K for i in xrange(1,num1+1)]
        self._inner_edges += [self.zpe + i*step2*self.I for i in xrange(1,num2+1)]
      if self.sz is not None: 
        num1,num2 = tuple(np.rint(self.sz * max_n).astype(int))
        step1,step2 = 1.0/(num1+1), 1.0/(num2+1)
        self._inner_edges += [self.xpe + i*step1*self.J for i in xrange(1,num1+1)]
        self._inner_edges += [self.ype + i*step2*self.I for i in xrange(1,num2+1)]
    return self._inner_edges

class Lattice:
  def __init__(self, stress_mesh, cunit_size, scale = 1):
    self.stress_mesh = stress_mesh
    self.cs = cunit_size
    self.scale = scale
    self.generate_cunits()

  def generate_cunits(self):
    self.dim = np.ceil(self.stress_mesh.bounds / self.cs).astype(int) + np.ones(3, dtype=int)
    print "Lattice Dimensions: " + " x ".join(list(self.dim.astype(str)))
    self.lattice_points = set()
    self.cunits = np.empty(self.dim, dtype = object)
    dp = np.array([0, self.cs / 2., self.cs / 2.])
    near_radius = self.stress_mesh.mesh_size * 0.49
    for i in xrange(self.dim[0]):
      for j in xrange(self.dim[1]):
        for k in xrange(self.dim[2]):
          point = np.array([i,j,k]) * self.cs + self.stress_mesh.min_p
          stress = [None] * 3
          void = 0
          for a in xrange(3):
            stress[a] = self.stress_mesh.nearest_stress(point+np.roll(dp,a), dist = near_radius)
            if stress[a] is None:
              void += 1
            else: 
              stress[a] = np.delete(stress[a],a)
              if self.scale != 1: stress[a] = np.minimum(stress[a] * self.scale, np.ones(2))
          if void == 3:
            continue
          else:
            self.lattice_points.add((i,j,k))
            self.cunits[i,j,k] = Cunit(np.array([i,j,k]), stress, self) 
      