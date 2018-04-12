# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FramePixels
                                 A QGIS plugin
 Draw a square around points matching pixels borders.
                              -------------------
        begin                : 2018-04-06
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Bruno Combal
        email                : bruno.combal@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from PyQt4.QtGui import QDialog
from qgis.gui import QgsFileWidget
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from frame_pixels_dialog import FramePixelsDialog
import frame_pixels_tools
import os.path
from osgeo import gdal, gdalconst, ogr

class FramePixels:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'FramePixels_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Frame Pixels')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'FramePixels')
        self.toolbar.setObjectName(u'FramePixels')

        # business variables
        self.outputPath = ''

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('FramePixels', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = FramePixelsDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/FramePixels/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Frame pixels'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.initWidgets()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Frame Pixels'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def initWidgets(self):
        self.dlg.widthSpinBox.lineEdit().setReadOnly(True)

        self.dlg.pointInputDialog.setFilter("*.shp")
        self.dlg.pointInputDialog.fileChanged.connect(self.getShapefile)

        self.dlg.rasterFileDialog.fileChanged.connect(self.getRasterfile)

        #self.dlg.outputFileDialog.setFilter("*.shp")
        #self.dlg.outputFileDialog.setStorageMode(1)

        self.dlg.buttonOutfile.clicked.connect(self.defineOutput)


        self.dlg.messageArea.setText('')

    def addExtension(self, fname, ext):
        thisExt = os.path.splitext(fname)[-1]
        if thisExt != ext:
            return '{}{}'.format(fname, ext)
        else:
            return fname

    def defineOutput(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        thisFile = dialog.getSaveFileName(self.dlg, "Define an ESRI shapefile name", self.outputPath, filter='*.shp') #os.path.expanduser("~"))
        if thisFile=='':
            return True
        outShapefile = self.addExtension(thisFile, '.shp')
        self.outputPath = os.path.basename(outShapefile)

        # once all ok, update text
        self.dlg.lineEditOutfile.setText(outShapefile)

        return True

    def getShapefile(self):
        inDataSource = ogr.Open(self.dlg.pointInputDialog.filePath(), 0)
        if inDataSource is None:
            return False
        inLayer = inDataSource.GetLayer()
        spatialRef = inLayer.GetSpatialRef()
        print 'spatial ref',spatialRef
        if spatialRef is None:
            self.dlg.messageInVector.setText('Unknown projection.')
        elif spatialRef == '':
            self.dlg.messageInVector.setText('Unknown projection.')
        else:
            self.dlg.messageInVector.setText('{}'.format(spatialRef))
        return True

    def getRasterfile(self):
        inRaster = gdal.Open(self.dlg.rasterFileDialog.filePath(), gdalconst.GA_ReadOnly)
        if inRaster is None:
            return False
        proj = inRaster.GetProjection()
        gt = inRaster.GetGeoTransform()
        self.dlg.messageInRaster.setText('Geotransform:{}\n{}\n'.format(gt, proj))
        inRaster = None
        return True

    def doProcessing(self, raster, inShapefile, npixels, outShapefile):
        # open raster
        inRaster = gdal.Open(raster, gdalconst.GA_ReadOnly)
        if inRaster is None:
            return False
        proj = inRaster.GetProjection()
        gt = inRaster.GetGeoTransform()
        #
        # !!! assumes vector and raster have same projections !!!
        # 
        # open vector
        inDataSource = ogr.Open(inShapefile, 0)
        if inDataSource is None:
            sys.exit(1)
        inLayer = inDataSource.GetLayer()
        spatialRef = inLayer.GetSpatialRef()

        # create output
        # vector out
        try:
            outDriver = ogr.GetDriverByName("ESRI Shapefile")
            outDS = outDriver.CreateDataSource(outShapefile)
            outLayer = outDS.CreateLayer("polygon", spatialRef, geom_type=ogr.wkbPolygon)
            if outLayer is None:
                raise("Could not create output file")
        except IOException, e:
            print "Could not create output file"
            print "{}".format(e)
            outDS = None
        # copy original fields to the output
        layerDefinition = inLayer.GetLayerDefn()
        for ii in range(layerDefinition.GetFieldCount()):
            fieldDefn = layerDefinition.GetFieldDefn(ii)
            print ii, fieldDefn.name
            outLayer.CreateField(fieldDefn)

        # now loop over all features
        for feature in inLayer:
            geom = feature.GetGeometryRef()
            # can take any input in, consider only the centroids.
            xx = geom.Centroid().GetX()
            yy = geom.Centroid().GetY()

            xStart, yStart, xEnd, yEnd = frame_pixels_tools.getPixelsSquareCorners(xx, yy, gt, npixels)

            poly = ogr.Geometry(ogr.wkbPolygon)
            ring = ogr.Geometry(ogr.wkbLinearRing)
            ring.AddPoint(xStart, yStart)
            ring.AddPoint(xEnd, yStart)
            ring.AddPoint(xEnd, yEnd)
            ring.AddPoint(xStart,yEnd)
            ring.AddPoint(xStart, yStart)
            poly.AddGeometry( ring )
            outFeature = ogr.Feature(outLayer.GetLayerDefn())
            outFeature.SetGeometry(poly)
            # copy over all input fields to the output layer
            for ii in range(layerDefinition.GetFieldCount()):
                outFeature.SetField(layerDefinition.GetFieldDefn(ii).GetNameRef(), feature.GetField(ii))
                outLayer.CreateFeature(outFeature)

            outFeature = None

        outLayer = None
        outDS = None

        return True

    def doCheckToGo(self):
        if not os.path.isfile(self.dlg.pointInputDialog.filePath()):
            self.dlg.messageArea.setText('Input vector file is not defined')
            return False

        if not os.path.isfile(self.dlg.rasterFileDialog.filePath()):
            self.dlg.messageArea.setText('Input raster file is not defined')
            return False

        if os.path.isfile(self.dlg.lineEditOutfile.text()): # try to remove it
            try:
                outDriver = ogr.GetDriverByName("ESRI Shapefile")
                if os.path.exists(self.outShapefile):
                    outDriver.DeleteDataSource(self.outShapefile)
            except IOError, e:
                self.dlg.messageArea.setText('Could not remove file {}'.format(self.outShapefile))
                return False
            return True

        if not os.path.isdir( os.path.dirname(self.dlg.lineEditOutfile.text()) ):
            self.dlg.messageArea.setText('Output directory {} does not exist'.format(os.path.dirname(self.dlg.lineEditOutfile.text())))
            return False

        return True

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        checkToGo = False
        while not checkToGo:
            runApp = self.dlg.exec_()
            # See if OK was pressed
            if runApp: # run=True, check if one can run
                checkToGo = self.doCheckToGo()
            else: # cancel=True
                checkToGo = True

        # See if OK was pressed
        if runApp:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            outShapefile = self.dlg.lineEditOutfile.text()
            #os.path.join(self.dlg.outputFileDialog.filePath(),'machin.shp' )
            self.dlg.messageArea.setText('Processing, please wait...')
            if self.doProcessing(self.dlg.rasterFileDialog.filePath(),
                self.dlg.pointInputDialog.filePath(),
                self.dlg.widthSpinBox.value(),
                outShapefile):
                if self.dlg.checkBoxOpenResult.checkState():
                    thisLayer = self.iface.addVectorLayer(outShapefile, "{}".format(os.path.basename(outShapefile).replace('.shp','')), "ogr")
            self.dlg.messageArea.setText('')

# end of code