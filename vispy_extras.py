import numpy as np

from vispy.visuals.line import LineVisual
from vispy.scene.node import Node


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