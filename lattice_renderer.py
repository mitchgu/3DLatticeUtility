import numpy as np
from vispy import color
from vispy.scene import SceneCanvas, cameras, visuals
from scene_nodes import CoolAxes, LatticeNode
from lattice import Lattice, Cunit
import copy, math

class LatticeRenderer:
  GROUND_COLOR = color.Color('#A2C9F5',0.6)
  GROUND_BORDER_COLOR = color.Color('#A2C9F5')
  VERTEX_COLOR = color.Color('#962420', 0.6)
  VERTEX_EDGE_COLOR = color.Color('#962420')
  PRINCIPAL_EDGE_COLOR = color.Color('#666')
  INNER_EDGE_COLOR = color.Color("#F59127")

  def __init__(self):
    self.canvas = SceneCanvas(
      title = "Lattice Visualizer",
      keys = 'interactive',
      size = (800, 600),
      show = True,
      bgcolor = color.Color("w")
      )
    self.canvas.measure_fps()

    # Set up a viewbox to display the cube with interactive arcball
    self.camera = cameras.ArcballCamera()
    self.view = self.canvas.central_widget.add_view(self.camera)

  def load_extras(self, bounds, cs):
    axes = CoolAxes(pos=(-2*cs,-2*cs,-cs),width=2,scale=cs)
    self.camera.center = bounds / 2
    self.camera.set_range((-cs,bounds[0]+cs),(-cs,bounds[1]+cs),(-cs,bounds[2]+cs))
    ground_plane = visuals.Rectangle(
      pos = (bounds[0] / 2, bounds[1] / 2, 0),
      color = self.GROUND_COLOR,
      width = bounds[0] + 2 * cs,
      height = bounds[1] + 2 * cs,
      border_color = self.GROUND_BORDER_COLOR
      )
    self.view.add(axes)
    self.view.add(ground_plane)

  def load_better_lattice(self, lattice, extrude_width):
    cs = lattice.cs
    bounds = lattice.dim * cs
    self.load_extras(bounds, cs)

    lattice_node = LatticeNode(lattice, extrude_width)
    self.view.add(lattice_node)

  def load_lattice(self, lattice, extrude_width):
    cs = lattice.cs
    bounds = lattice.dim * cs
    self.load_extras(bounds, cs)

    lps = lattice.lattice_points
    p = np.array(list(lps)) * cs
    vertex_set = set()
    principal_edge_set = set()
    inner_edge_list = []
    for lp in lps:
      cunit = lattice.cunits[lp]
      vertex_set = vertex_set | cunit.vertices
      principal_edge_set = principal_edge_set | cunit.principal_edges
      inner_edge_list += cunit.inner_edges(max_inner_edges)
    print "# of vertices: " + str(len(vertex_set))
    print "# of principal edges: " + str(len(principal_edge_set))
    print "# of inner edges: " + str(len(inner_edge_list))
    vertices = visuals.Markers()
    vertices.set_data(
      pos = np.array(list(vertex_set)) * cs,
      size = 5,
      face_color = self.VERTEX_COLOR,
      edge_color = self.VERTEX_EDGE_COLOR
      )
    principal_edges = visuals.Line(
      np.array(list(principal_edge_set)) * cs,
      connect='segments',
      antialias=True,
      color=self.PRINCIPAL_EDGE_COLOR
      )
    inner_edges=visuals.Line(
      np.array(inner_edge_list) * cs,
      connect='segments',
      antialias=True,
      color=self.INNER_EDGE_COLOR
      )
    self.view.add(vertices)
    self.view.add(principal_edges)
    self.view.add(inner_edges)

  def render(self):
    self.canvas.app.run()

  """# Implement key presses
  @canvas.events.key_press.connect
  def on_key_press(event):
    if event.text == '1':
      self.camera.reset()"""

if __name__ == '__main__':
    canvas.app.run()
