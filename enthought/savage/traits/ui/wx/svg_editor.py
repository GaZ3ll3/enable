#-------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Bryce Hendrix
#  Date:   08/06/2008
#
#-------------------------------------------------------------------------------

""" Traits UI 'display only' image editor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------
from enthought.traits.api import Instance, Int, Enum
from enthought.traits.ui.wx.editor import Editor
from enthought.traits.ui.wx.basic_editor_factory import BasicEditorFactory
    

from enthought.savage.svg.document import SVGDocument

from enthought.etsconfig.api import ETSConfig

from enthought.savage.svg.backends.wx.renderer import Renderer as WxRenderer
from enthought.savage.svg.backends.kiva.renderer import Renderer as KivaRenderer

from kiva_render_panel import RenderPanel as KivaRenderPanel
if ETSConfig.toolkit == 'wx':
    from wx_render_panel import RenderPanel as WxRenderPanel
else:
    import warnings
    warning.warn("Only 'wx' toolkit is supported currently, falling back to Kiva backend")
    from kiva_render_panel import RenderPanel as WxRenderPanel
    


#-------------------------------------------------------------------------------
#  '_SVGEditor' class:
#-------------------------------------------------------------------------------
                               
class _SVGEditor ( Editor ):
    """ Traits UI 'display only' image editor.
    """
    
    scrollable = True
    
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        document = self.value
        
        # TODO: the document should not know about the renderer, this should
        # be an attribute of the editor
        
        if document.renderer == WxRenderer:
            self.control = WxRenderPanel( parent, document=document)
        else:
            self.control = KivaRenderPanel( parent, document=document)
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if self.control.document != self.value:
            self.control.document = self.value
            self.control.Refresh()
                    
#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------
class SVGEditor ( BasicEditorFactory ):
    
    # The editor class to be created:
    klass = _SVGEditor