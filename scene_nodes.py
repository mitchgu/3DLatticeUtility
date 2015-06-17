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
  axis_map = {'x': 0, 'y': 1, 'z': 2}

  def __init__(self, lattice, extrude_width, shown, parent=None, name=None):
    Node.__init__(self, parent, name)
    self.lattice = lattice
    self.slice_all = slice(0,np.amax(lattice.dim),None)
    self.max_inner_edges = int(math.floor(float(lattice.cs) / extrude_width) - 1)
    self.cunit_nodes = np.empty(lattice.dim, dtype = object)
    self.set_transform('st', scale = np.ones(3) * lattice.cs, translate = np.ones(3) * 0.1)
    for lp in lattice.lattice_points:
      current_cunit = CunitNode(lattice.cunits[lp], self.max_inner_edges, parent=self)
      current_cunit.set_transform('st', translate = np.array(lp))
      self.cunit_nodes[lp] = current_cunit
    self.hide()
    self.show(shown)
    self.shown = list(shown)

  def filter_cunit_nodes(self, i,j,k):
    if i == None: i = self.slice_all
    if j == None: j = self.slice_all
    if k == None: k = self.slice_all
    filtered = self.cunit_nodes[i,j,k]
    if isinstance(filtered, CunitNode):
      filtered = np.array([filtered])
    return filtered

  def show_hide(self, mode, coords):
    i,j,k = coords
    selected_cunits = self.filter_cunit_nodes(i,j,k)
    if selected_cunits is None: return
    else: selected_cunits = selected_cunits.flatten()
    for i in xrange(selected_cunits.size):
      cu = selected_cunits[i]
      if cu is not None:
        if mode:
          cu.show()
        else:
          cu.hide()

  def show(self, coords=(None,None,None)):
    self.show_hide(True, coords)

  def hide(self, coords=(None,None,None)):
    self.show_hide(False, coords)

  def change_visible(self, axis, up_or_down):
    self.hide(self.shown)
    axis = self.axis_map[axis]
    if up_or_down == 'up':
      if self.shown[axis] is None:
        self.shown[axis] = 0
      elif self.shown[axis] < self.lattice.dim[axis] - 1:
        self.shown[axis] += 1
    elif up_or_down == 'down':
      if self.shown[axis] is None:
        self.shown[axis] = self.lattice.dim[axis] - 1
      elif self.shown[axis] > 0:
        self.shown[axis] -= 1
    elif up_or_down == 'all':
      self.shown[axis] = None
    self.show(self.shown)

class CunitNode(Node):
  VERTEX_COLOR = color.Color('#962420', 0.6)
  VERTEX_EDGE_COLOR = color.Color('#962420', 0.99)
  PRINCIPAL_EDGE_COLOR = color.Color('#666', 0.99)
  INNER_EDGE_COLOR = color.Color("#F59127", 0.99)

  def __init__(self, cu, max_n, parent=None, name=None):
    Node.__init__(self, parent, name)
    cu.vertex = np.zeros(3)
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
      )
    self.inner_edges.visible = False

  def show(self):
    self.markers.visible = True
    self.principal_edges.visible = True
    self.inner_edges.visible = True

  def hide(self):
    self.markers.visible = False
    self.principal_edges.visible = False
    self.inner_edges.visible = False

