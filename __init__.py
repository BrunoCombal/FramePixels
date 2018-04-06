# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FramePixels
                                 A QGIS plugin
 Draw a square around points matching pixels borders.
                             -------------------
        begin                : 2018-04-06
        copyright            : (C) 2018 by Bruno Combal
        email                : bruno.combal@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load FramePixels class from file FramePixels.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .frame_pixels import FramePixels
    return FramePixels(iface)
