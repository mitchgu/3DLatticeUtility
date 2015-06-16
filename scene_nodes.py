import numpy as np
import math
from vispy.visuals.line import LineVisual
from vispy.scene.node import Node
from vispy.scene import visuals
from vispy import color
from lattice import Lattice, Cunit

class CoolAxesVisual(LineVisual):
  """
  Simple 3D axis for indicating coordinate system orientation. Axes are
  x=red, y=green, z=blue.
  """
  def __init__(self, **kwargs):
    pos = np.asarray(kwargs.pop('pos', (0,0,0)))
    width = kwargs.pop('width', 1)
    scale = kwargs.pop('scale', 1)
    verts = np.array([[0, 0, 0],
                      [1, 0, 0],
                      [0, 0, 0],
                      [0, 1, 0],
                      [0, 0, 0],
                      [0, 0, 1]]) * scale + pos
    color = np.array([[1, 0, 0, 1],
                      [1, 0, 0, 1],
                      [0, 1, 0, 1],
                      [0, 1, 0, 1],
                      [0, 0, 1, 1],
                      [0, 0, 1, 1]])
    LineVisual.__init__(self, pos=verts, color=color, width = width, connect='segments',
                        method='gl', **kwargs)

class CoolAxes(Node,CoolAxesVisual):
  def __init__(self, *args, **kwargs):
    parent = kwargs.pop('parent', None)
    name = kwargs.pop('name', None)
    self.name = name  # to allow __str__ before Node.__init__
    CoolAxesVisual.__init__(self, *args, **kwargs)
    Node.__init__(self, parent=parent, name=name)

class LatticeNode(Node):
  def __init__(self, lattice, extrude_width, parent=None, name=None):
    self.name = name  # to allow __str__ before Node.__init__
    Node.__init__(self, parent, name)
    self.lattice = lattice
    self.max_inner_edges = int(math.floor(float(lattice.cs) / extrude_width) - 1)
    self.cunit_nodes = np.empty(lattice.dim, dtype = object)
    self.create_cunit_nodes()

  def create_cunit_nodes(self):
    lps = self.lattice.lattice_points
    for lp in lps:
      current_cunit = CunitNode(self.lattice.cunits[lp], self.max_inner_edges, parent=self)
      current_cunit.set_transform(
        'st',
        translate = np.array(lp) * self.lattice.cs,
        scale = np.ones(3) * self.lattice.cs)
      self.cunit_nodes[lp] = current_cunit

class CunitNode(Node):
  VERTEX_COLOR = color.Color('#962420', 0.6)
  VERTEX_EDGE_COLOR = color.Color('#962420')
  PRINCIPAL_EDGE_COLOR = color.Color('#666')
  INNER_EDGE_COLOR = color.Color("#F59127")

  def __init__(self, cu, max_n, parent=None, name=None):
    self.name = name  # to allow __str__ before Node.__init__
    Node.__init__(self, parent, name)
    self.cu = cu
    self.markers = visuals.Markers(parent=self)
    self.markers.set_data(
      pos = np.array(list(cu.vertices)),
      size = 4,
      face_color = self.VERTEX_COLOR,
      edge_color = self.VERTEX_EDGE_COLOR
      )
    cu_principal_edges = np.array(list(cu.principal_edges))
    self.principal_edges = visuals.Line(
      np.array(list(cu_principal_edges)),
      connect='segments',
      antialias=True,
      color=self.PRINCIPAL_EDGE_COLOR,
      parent = self
      )
    cu_inner_edges = np.array(cu.inner_edges(max_n))
    self.inner_edges = visuals.Line(
      np.array(cu_inner_edges),
      connect='segments',
      antialias=True,
      color=self.INNER_EDGE_COLOR,
      parent = self
      ) if len(cu_inner_edges) != 0 else None

