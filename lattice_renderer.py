import numpy as np
from vispy.color import ColorArray
from vispy.scene import SceneCanvas, cameras, visuals
from scene_nodes import CoolAxes, LatticeNode, DynamicLatticeNode
from lattice import Lattice, Cunit
import copy, math

class LatticeRenderer:
  BACKGROUND_COLOR = ColorArray('w')
  GROUND_COLOR = ColorArray('#A2C9F5',0.6)
  GROUND_BORDER_COLOR = ColorArray('#A2C9F5')
  d_lattice_node = None
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
    max_n = int(math.floor(float(lattice.cs) / extrude_width) - 1)
    self.load_environment(lattice.dim, lattice.cs)
    self.d_lattice_node = DynamicLatticeNode(lattice, max_n, (0,0,0))
    self.view.add(self.d_lattice_node)
    self.lattice_node = LatticeNode(lattice, max_n, True)
    self.view.add(self.lattice_node)

  def load_lattice(self, lattice, extrude_width):
    max_n = int(math.floor(float(lattice.cs) / extrude_width) - 1)
    self.load_environment(lattice.dim, lattice.cs)
    self.lattice_node = LatticeNode(lattice, max_n)
    self.view.add(self.lattice_node)

  def reset_camera(self):
    self.camera.reset()
  def visible_x_up(self): 
    if self.d_lattice_node: self.d_lattice_node.change_visible('x','up')
  def visible_x_down(self): 
    if self.d_lattice_node: self.d_lattice_node.change_visible('x','down')
  def visible_x_all(self): 
    if self.d_lattice_node: self.d_lattice_node.change_visible('x','all')
  def visible_y_up(self): 
    if self.d_lattice_node: self.d_lattice_node.change_visible('y','up')
  def visible_y_down(self): 
    if self.d_lattice_node: self.d_lattice_node.change_visible('y','down')
  def visible_y_all(self): 
    if self.d_lattice_node: self.d_lattice_node.change_visible('y','all')
  def visible_z_up(self): 
    if self.d_lattice_node: self.d_lattice_node.change_visible('z','up')
  def visible_z_down(self): 
    if self.d_lattice_node: self.d_lattice_node.change_visible('z','down')
  def visible_z_all(self): 
    if self.d_lattice_node: self.d_lattice_node.change_visible('z','all')

  def render(self):
    self.canvas.app.run()

if __name__ == '__main__':
    canvas.app.run()
