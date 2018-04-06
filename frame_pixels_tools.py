# author: Bruno Combal
# functions to go from/to pixel coordinates and map coordinates

def ApplyGeoTransform(inx, iny, gt):
    ''' Apply a geotransform
        @param  inx       Input x coordinate (double)
        @param  iny       Input y coordinate (double)
        @param  gt        Input geotransform (six doubles)
        @return outx,outy Output coordinates (two doubles)
    '''
    outx = gt[0] + inx * gt[1] + iny * gt[2]
    outy = gt[3] + inx * gt[4] + iny * gt[5]
    return (outx, outy)

def InvGeoTransform(gt_in):
    # we assume a 3rd row that is [1 0 0]
    # Compute determinate
    det = gt_in[1] * gt_in[5] - gt_in[2] * gt_in[4]

    if (abs(det) < 0.000000000000001):
        return

    inv_det = 1.0 / det

    # compute adjoint, and divide by determinate
    gt_out = [0, 0, 0, 0, 0, 0]
    gt_out[1] = gt_in[5] * inv_det
    gt_out[4] = -gt_in[4] * inv_det

    gt_out[2] = -gt_in[2] * inv_det
    gt_out[5] = gt_in[1] * inv_det

    gt_out[0] = (gt_in[2] * gt_in[3] - gt_in[0] * gt_in[5]) * inv_det
    gt_out[3] = (-gt_in[1] * gt_in[3] + gt_in[0] * gt_in[4]) * inv_det

    return gt_out

def mapToPixel(mx, my, gt):
	if gt[2] + gt[4] == 0:  # Simple calc, no inversion required
		px = (mx - gt[0]) / gt[1]
		py = (my - gt[3]) / gt[5]
	else:
		px, py = ApplyGeoTransform(mx, my, InvGeoTransform(gt))
	return int(px + 0.5), int(py + 0.5)

def pixelToMap(px, py, gt):
	mx, my = ApplyGeoTransform(px, py, gt)
	return mx, my

# get coordinates of a square of N pixels width around coordinate (x, y)
def getPixelsSquareCorners(x, y, GT, N):
    # get pixels positions
    xPix, yPix = mapToPixel(x, y, GT)
    xStartPix = xPix - N/2
    yStartPix = yPix + N/2
    # for the lower left bound, take coordinates of the upper left corner of the next pixel
    xEndPix = xPix + N/2 + 1 
    yEndPix = yPix - N/2 -1
    # convert back to coordinates
    xStart, yStart = pixelToMap(xStartPix, yStartPix, GT)
    xEnd, yEnd = pixelToMap(xEndPix, yEndPix, GT)
    return xStart, yStart, xEnd, yEnd