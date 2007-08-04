""" Defines a Viewport which renders sub-areas of components """

# Standard library imports
from numpy import array
from sets import Set

# Enthought library traits
from enthought.enable2.traits.rgba_color_trait import RGBAColor
from enthought.traits.api import false, Instance

# Local relative imports
from enable_traits import bounds_trait, coordinate_trait
from base import empty_rectangle, intersect_bounds
from component import Component
from container import Container



class Viewport(Component):
    """
    A "window" or "view" into a sub-region of another component.
    """

    # The component we are viewing
    component = Instance(Component)

    # The position of our viewport into our component (in the component's
    # coordinate space)
    view_position = coordinate_trait

    # The bounds of our viewport in the space of our component
    view_bounds = bounds_trait

    # Whether or not this viewport should stay constrained to the bounds
    # of the viewed component
    # TODO: Implement this
    stay_inside = false

    # Our default background to render if component is None or if we
    # are viewing outside the component
    bg_color = RGBAColor( (1.0, 1.0, 1.0, 1.0) )


    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, **traits):
        Component.__init__(self, **traits)
        _prev_event_handlers = Set()
        return

    def components_at(self, x, y, add_containers = False):
        """
        Returns the list of components inside the viewport at the given (x,y)
        in the viewport's native coordinate space (not in the space of the
        component it is viewing).

        Although Viewports are not containers, they support this method.
        """
        if self.is_in(x, y):
            if self.component is not None:
                x_trans = x + self.view_position[0]
                y_trans = y + self.view_position[1]
                if isinstance(self.component, Container):
                    return self.component.components_at(x_trans, y_trans)
                elif self.component.is_in(x_trans, y_trans):
                    return [self.component]
                else:
                    return []
        else:
            return []

    def cleanup(self, window):
        """When a window viewing or containing a component is destroyed,
        cleanup is called on the component to give it the opportunity to
        delete any transient state it may have (such as backbuffers)."""
        if self.component:
            self.component.cleanup(window)

    #------------------------------------------------------------------------
    # Component interface
    #------------------------------------------------------------------------

    def _draw(self, gc, view_bounds=None, mode="default"):
        # For now, ViewPort ignores the view_bounds that are passed in...
        # Long term, it should be intersected with the view_position to
        # compute a new view_bounds to pass in to our component.
        if self.component is not None:
            x, y = self.position
            view_x, view_y = self.view_position
            gc.save_state()
            gc.translate_ctm(int(x - view_x), int(y - view_y))
            gc.clip_to_rect(view_x-0.5, view_y-0.5, self.view_bounds[0]+1, self.view_bounds[1]+1)
            # transform the passed-in view_bounds; this is not the same thing as
            # self.view_bounds!

            if view_bounds:
                # Find the intersection rectangle of the viewport with the view_bounds,
                # and transform this into the component's space.
                clipped_view = intersect_bounds(self.position + self.bounds, view_bounds)
                if clipped_view != empty_rectangle:
                    # clipped_view and self.position are in the space of our parent
                    # containers.  we know that self.position -> view_x,view_y
                    # in the coordinate space of our component.  So, find the
                    # vector from self.position to clipped_view, then add this to
                    # view_x and view_y to generate the transformed coordinates
                    # of clipped_view in our component's space.
                    offset = array(clipped_view[:2]) - array(self.position)
                    new_bounds = (offset[0]+view_x, offset[1]+view_y,
                                  clipped_view[2], clipped_view[3])
                    self.component.draw(gc, new_bounds, mode=mode)
                else:
                    pass

            gc.restore_state()
        else:
            pass
        return

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _component_changed(self, old, new):
        if (old is not None) and (self in old.viewports):
            old.viewports.remove(self)

        if (new is not None) and (self not in new.viewports):
            new.viewports.append(self)
        return

    def _bounds_changed(self, old, new):
        Component._bounds_changed(self, old, new)
        self.set(view_bounds = new, trait_change_notify=False)
        return

    def _bounds_items_changed(self, event):
        return self._bounds_changed(None, self.bounds)

    def _view_bounds_changed(self, old, new):
        self.set(bounds = new, trait_change_notify=False)
        return

    def _view_bounds_items_changed(self, event):
        return self._view_bounds_changed(None, self.bounds)

    def _dispatch_stateful_event(self, event, suffix):
        if isinstance(self.component, Component):
            event.offset_xy(-self.view_position[0]+ self.position[0], -self.view_position[1] + self.position[1])
            try:
                self.component.dispatch(event, suffix)
            finally:
                event.pop()
        return


# EOF
