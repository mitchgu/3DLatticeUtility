import numpy as np
from vispy.color import ColorArray
from vispy.scene import SceneCanvas, cameras, visuals
from scene_nodes import CoolAxes, LatticeNode
from lattice import Lattice, Cunit
import copy, math

class LatticeRenderer:
  BACKGROUND_COLOR = ColorArray('w')
  GROUND_COLOR = ColorArray('#A2C9F5',0.6)
  GROUND_BORDER_COLOR = ColorArray('#A2C9F5')
  lattice_node = None

  def __init__(self):
    self.canvas = SceneCanvas(
      title = "Lattice Visualizer",
      keys = 'interactive',
      size = (800, 600),
      show = True,
      bgcolor = self.BACKGROUND_COLOR
      )
    self.canvas.measure_fps()
    self.key_functions = {
      '1': self.reset_camera,
      'd': self.visible_x_up,
      'a': self.visible_x_down,
      'z': self.visible_x_all,
      'w': self.visible_y_up,
      's': self.visible_y_down,
      'x': self.visible_y_all,
      'e': self.visible_z_up,
      'q': self.visible_z_down,
      'c': self.visible_z_all
    }

    # Register key press events
    @self.canvas.events.key_press.connect
    def on_key_press(event):
      if event.text in self.key_functions:
        self.key_functions[event.text]()

    # Set up a viewbox to display the cube with interactive arcball
    self.camera = cameras.ArcballCamera()
    self.view = self.canvas.central_widget.add_view(self.camera)

  def load_environment(self, dim, cs):
    bounds = dim * cs
    axes = CoolAxes(pos=(-2*cs,-2*cs,-cs),width=2,scale=cs)
    self.camera.center = bounds / 2
    self.camera.set_range((-cs,bounds[0]+cs),(-cs,bounds[1]+cs),(-cs,bounds[2]+cs))
    self.camera.set_default_state()
    ground_plane = visuals.Rectangle(
      pos = (bounds[0] / 2, bounds[1] / 2, 0),
      color = self.GROUND_COLOR,
      width = bounds[0] + 2 * cs,
      height = bounds[1] + 2 * cs,
      border_color = self.GROUND_BORDER_COLOR
      )
    self.view.add(axes)
    self.view.add(ground_plane)

  def load_dynamic_lattice(self, lattice, extrude_width):
    self.load_environment(lattice.dim, lattice.cs)
    self.lattice_node = LatticeNode(lattice, extrude_width, (0,0,0))
    self.view.add(self.lattice_node)
    self.load_lattice(lattice, extrude_width, True)

  def load_lattice(self, lattice, extrude_width, faded = False):
    VERTEX_COLOR = ColorArray('#962420', 0.6)
    VERTEX_EDGE_COLOR = ColorArray('#962420')
    PRINCIPAL_EDGE_COLOR = ColorArray('#666')
    INNER_EDGE_COLOR = ColorArray("#F59127")
    if faded: 
      VERTEX_COLOR.alpha = 0.2
      VERTEX_EDGE_COLOR.alpha = 0.2
      PRINCIPAL_EDGE_COLOR.alpha = 0.2
      INNER_EDGE_COLOR.alpha = 0.2
    cs = lattice.cs
    self.load_environment(lattice.dim, cs)
    max_inner_edges = int(math.floor(float(lattice.cs) / extrude_width) - 1)

    lps = lattice.lattice_points
    p = np.array(list(lps)) * cs
    vertex_set = set()
    principal_edge_set = set()
    inner_edge_list = []
    for lp in lps:
      cunit = lattice.cunits[lp]
      cunit.vertex = np.array(lp)
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
      face_color = VERTEX_COLOR,
      edge_color = VERTEX_EDGE_COLOR
      )
    principal_edges = visuals.Line(
      np.array(list(principal_edge_set)) * cs,
      connect='segments',
      antialias=True,
      color=PRINCIPAL_EDGE_COLOR
      )
    inner_edges=visuals.Line(
      np.array(inner_edge_list) * cs,
      connect='segments',
      antialias=True,
      color=INNER_EDGE_COLOR
      )
    self.view.add(vertices)
    self.view.add(principal_edges)
    if not faded: self.view.add(inner_edges)

  def reset_camera(self):
    self.camera.reset()
  def visible_x_up(self): 
    if self.lattice_node: self.lattice_node.change_visible('x','up')
  def visible_x_down(self): 
    if self.lattice_node: self.lattice_node.change_visible('x','down')
  def visible_x_all(self): 
    if self.lattice_node: self.lattice_node.change_visible('x','all')
  def visible_y_up(self): 
    if self.lattice_node: self.lattice_node.change_visible('y','up')
  def visible_y_down(self): 
    if self.lattice_node: self.lattice_node.change_visible('y','down')
  def visible_y_all(self): 
    if self.lattice_node: self.lattice_node.change_visible('y','all')
  def visible_z_up(self): 
    if self.lattice_node: self.lattice_node.change_visible('z','up')
  def visible_z_down(self): 
    if self.lattice_node: self.lattice_node.change_visible('z','down')
  def visible_z_all(self): 
    if self.lattice_node: self.lattice_node.change_visible('z','all')

  def render(self):
    self.canvas.app.run()

if __name__ == '__main__':
    canvas.app.run()
