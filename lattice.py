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

  def __init__(self, vertex, stress, max_n):
    self.vertex = vertex
    self.stress = stress
    self.max_n = max_n
    self.sx = stress[0]
    self.sy = stress[1]
    self.sz = stress[2]
    self.xpe = np.array([self.vertex, self.vertex + self.I])
    self.ype = np.array([self.vertex, self.vertex + self.J])
    self.zpe = np.array([self.vertex, self.vertex + self.K])
    self.VERTEX_OFFSETS = [
      [self.J, self.K, self.J + self.K],
      [self.I, self.K, self.I + self.K],
      [self.I, self.J, self.I + self.J]]
    self.PRINCIPAL_EDGES = [
      [self.ype, self.zpe, self.ype + self.K, self.zpe + self.J],
      [self.xpe, self.zpe, self.xpe + self.K, self.zpe + self.I],
      [self.xpe, self.ype, self.xpe + self.J, self.ype + self.I]]
    self.INNER_EDGE_OFFSETS = [
      [[self.ype, self.K], [self.zpe, self.J]],
      [[self.xpe, self.K], [self.zpe, self.I]],
      [[self.xpe, self.J], [self.ype, self.I]]]
    self.plane_vertices = [self.calc_plane_vertices(i) for i in xrange(3)]
    self.plane_principal_edges = [self.calc_plane_principal_edges(i) for i in xrange(3)]
    self.plane_inner_edges = [self.calc_plane_inner_edges(i) for i in xrange(3)]

  def __str__(self):
    return str(self.stress)

  def calc_plane_vertices(self, plane_index):
    plane_vertices = []
    if self.stress[plane_index] is not None:
      for offset in self.VERTEX_OFFSETS[plane_index]:
        plane_vertices.append(tuple(self.vertex + offset))
    return plane_vertices

  def calc_plane_principal_edges(self, plane_index):
    plane_principal_edges = []
    if self.stress[plane_index] is not None:
      toTuple = lambda a: tuple(map(tuple,a))
      for edge in self.PRINCIPAL_EDGES[plane_index]:
        plane_principal_edges.append(toTuple(edge))
    return plane_principal_edges

  def calc_plane_inner_edges(self, plane_index):
    plane_inner_edges = []
    if self.stress[plane_index] is not None:
      num1,num2 = tuple(np.rint(self.stress[plane_index] * self.max_n).astype(int))
      step1,step2 = 1.0/(num1 + 1), 1.0 / (num2 + 1)
      offsets = self.INNER_EDGE_OFFSETS[plane_index]
      plane_inner_edges += [offsets[0][0] + i*step1*offsets[0][1] for i in xrange(1, num1+1)]
      plane_inner_edges += [offsets[1][0] + i*step2*offsets[1][1] for i in xrange(1, num2+1)]
    return plane_inner_edges
  
  @property
  def vertices(self):
    if True:
      vertices = set([tuple(self.vertex)])
      vertices = vertices | set(self.plane_vertices[0])
      vertices = vertices | set(self.plane_vertices[1])
      vertices = vertices | set(self.plane_vertices[2])
    return vertices

  @property
  def principal_edges(self):
    if True:
      principal_edges = set()
      principal_edges = principal_edges | set(self.plane_principal_edges[0])
      principal_edges = principal_edges | set(self.plane_principal_edges[1])
      principal_edges = principal_edges | set(self.plane_principal_edges[2])
    return principal_edges

  @property
  def inner_edges(self):
    if True:
      inner_edges = [np.array([self.vertex,self.vertex])] # just so it's not none
      inner_edges += self.plane_inner_edges[0]
      inner_edges += self.plane_inner_edges[1]
      inner_edges += self.plane_inner_edges[2]
      return inner_edges

class Lattice:
  def __init__(self, stress_mesh, cunit_size, max_n, scale = 1):
    self.stress_mesh = stress_mesh
    self.cs = cunit_size
    self.max_n = max_n
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
            self.cunits[i,j,k] = Cunit(np.array((i,j,k)), stress, self.max_n)
      