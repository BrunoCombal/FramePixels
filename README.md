# Frame Pixels
A plugin to draw square matching pixels borders.
The interest of the plugin is to allow to draw squares cropping exactly the pixels (the square borders do not cut pixels in two), allowing from a random draw of point to defines areas matching exactly the pixels in the raster.
This is of use for defining validation plans, or sampling strategy, by cancelling uncertainty about what is collected from a square not matching exactly pixels borders.

The plugin takes in input:
- A shapefile of points;
- A raster file.
- The size of the output square polygons to draw around the points, as a number of pixels of the input image.

Each point of the input vector file is located on a pixel of the input raster; this pixel will be the center of the squares to draw, each square having to match the border of the pixels. As the pixel selected by the input points is the center of the square to draw, the size of the square (its width) must be an odd number of pixels.

More information: https://github.com/BrunoCombal/PointToPolygon/wiki