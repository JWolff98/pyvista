"""Contains the BackgroundRenderer class"""
import vtk
import numpy as np

from .renderer import Renderer
import pyvista

class BackgroundRenderer(Renderer):
    """BackgroundRenderer for visualizing a backgroud image."""

    def __init__(self, parent, scale, image_path, as_global=True, view_port=None):
        # read the image first as we don't need to create a render if
        # the image path is invalid
        image_data = pyvista.read(image_path)

        super(BackgroundRenderer, self).__init__(parent, border=False)
        self.SetLayer(0)
        self.InteractiveOff()
        self.SetBackground(self.parent.renderer.GetBackground())
        self._scale = scale
        self._modified_observer = None
        self._prior_window_size = None
        if view_port is not None:
            self.SetViewport(view_port)

        # create image actor
        image_actor = vtk.vtkImageActor()
        image_actor.SetInputData(image_data)
        self.add_actor(image_actor, name='background')
        self.camera.ParallelProjectionOn()
        self.resize()

    def resize(self, *args):
        """Resize a background renderer"""
        if self.parent is None:  # when deleted
            return

        if self._prior_window_size != self.parent.window_size:
            self._prior_window_size = self.parent.window_size

        actor = self._actors['background']
        image_data = actor.GetInput()
        origin = image_data.GetOrigin()
        extent = image_data.GetExtent()
        spacing = image_data.GetSpacing()
        xc = origin[0] + 0.5*(extent[0] + extent[1]) * spacing[0]
        yc = origin[1] + 0.5*(extent[2] + extent[3]) * spacing[1]
        yd = (extent[3] - extent[2] + 1) * spacing[1]
        d = self.camera.GetDistance()

        # make the longest dimensions match the plotting window
        img_dim = np.array(image_data.dimensions[:2])
        self.camera.SetFocalPoint(xc, yc, 0.0)
        self.camera.SetPosition(xc, yc, d)

        ratio = img_dim/np.array(self.parent.window_size)
        scale_value = 1
        if ratio.max() > 1:
            # images are not scaled if larger than the window
            scale_value = ratio.max()

        if self._scale is not None:
            scale_value /= self._scale

        self.camera.SetParallelScale(0.5 * yd * scale_value)