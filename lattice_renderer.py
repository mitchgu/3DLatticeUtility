import numpy as np
from vispy import scene, color
from vispy.scene import SceneCanvas, cameras, visuals
from vispy_extras import CoolAxes
from lattice import Lattice, Cunit
import copy, math

class LatticeRenderer:
  GROUND_COLOR = color.Color('#A2C9F5',0.6)
  GROUND_BORDER_COLOR = color.Color('#A2C9F5')
  VERTEX_COLOR = color.Color('#962420', 0.6)
  VERTEX_EDGE_COLOR = color.Color('#962420')
  PRINCIPAL_EDGE_COLOR = color.Color('#666')
  INNER_EDGE_COLOR = 'b'

  def __init__(self):
    self.canvas = SceneCanvas(
      title = "Lattice Renderer",
      keys = 'interactive',
      size = (800, 600),
      show = True,
      bgcolor = color.Color("w")
      )
    self.canvas.measure_fps()

    # Set up a viewbox to display the cube with interactive arcball
    self.camera = cameras.ArcballCamera()
    self.view = self.canvas.central_widget.add_view(self.camera)

  def load_lattice(self, lattice, extrude_width):
    cw = lattice.cunit_width
    bounds = lattice.dim * cw
    max_inner_edges = math.floor(float(cw) / extrude_width) - 1

    axes = CoolAxes(pos=(-2*cw,-2*cw,-cw),width=2,scale=cw)
    self.camera.center = bounds / 2
    self.camera.set_range((-cw,bounds[0]+cw),(-cw,bounds[1]+cw),(-cw,bounds[2]+cw))
    ground_plane = visuals.Rectangle(
      pos = (bounds[0] / 2, bounds[1] / 2, 0),
      color = self.GROUND_COLOR,
      width = bounds[0] + 2 * cw,
      height = bounds[1] + 2 * cw,
      border_color = self.GROUND_BORDER_COLOR
      )
    self.view.add(axes)
    self.view.add(ground_plane)

    lps = lattice.lattice_points
    p = np.array(list(lps)) * cw
    vertex_set = set()
    principal_edge_set = set()
    for lp in lps:
      cunit = lattice.cunits[lp]
      vertex_set = vertex_set | cunit.vertices
      principal_edge_set = principal_edge_set | cunit.principal_edges
    vertices = visuals.Markers()
    vertices.set_data(pos = np.array(list(vertex_set)) * cw, size = 5, face_color = self.VERTEX_COLOR, edge_color = self.VERTEX_EDGE_COLOR)
    principal_edges = visuals.Line(np.array(list(principal_edge_set)) * cw, connect='segments', antialias=True, color=self.PRINCIPAL_EDGE_COLOR, width=1.5)
    #inner_edges = visuals.Line
    self.view.add(vertices)
    self.view.add(principal_edges)

  def render(self):
    self.canvas.app.run()

  """# Implement key presses
  @canvas.events.key_press.connect
  def on_key_press(event):
    if event.text == '1':
      self.camera.reset()"""

if __name__ == '__main__':
    canvas.app.run()
