from cv2 import distanceTransform, minMaxLoc, normalize, \
                DIST_L2, DIST_MASK_5, NORM_MINMAX
from cv2.typing import MatLike

def euclideanDistanceTransform(binImg: MatLike,
                               distanceType: int = DIST_L2,
                               maskSize: int = DIST_MASK_5) -> tuple:
    """
    Calculates euclidean distance between each non-zero pixel and nearest
    zero pixel in a binary image. Returns location of non-zero pixel with
    largest distance to nearest zero pixel.

    Parameters
    ----------
    binImg: MatLike
        binary image

    distanceType: int
        distance type used to calculate distance (default: cv2.DIST_L2)

    maskSize: int
        mask size used to calculate distance (default: cv2.DIST_MASK_5)

    Returns
    -------
    maxLoc: tuple
        location of non-zero pixel with largest distance to nearest zero
        pixel
    """
    dist = distanceTransform(src = binImg,
                             distanceType = distanceType,
                             maskSize = maskSize,
                             dst = None,
                             dstType = None)
    _, _, _, maxLoc = minMaxLoc(src = dist,
                                mask = None)
    return maxLoc

def euclideanDistanceTransformNorm1(binImg: MatLike,
                                    distanceType: int = DIST_L2,
                                    maskSize: int = DIST_MASK_5) -> tuple:
    """
    Calculates euclidean distance between each non-zero pixel and nearest
    zero pixel in a binary image. Returns location of non-zero pixel with
    largest distance to nearest zero pixel.
    Pixel values normalized between [0, 1].

    Parameters
    ----------
    binImg: MatLike
        binary image

    distanceType: int
        distance type used to calculate distance (default: cv2.DIST_L2)

    maskSize: int
        mask size used to calculate distance (default: cv2.DIST_MASK_5)

    Returns
    -------
    maxLoc: tuple
        location of non-zero pixel with largest distance to nearest zero
        pixel
    """
    dist = distanceTransform(src = binImg,
                             distanceType = distanceType,
                             maskSize = maskSize,
                             dst = None,
                             dstType = None)
    distNorm = normalize(src = dist,
                         dst = None,
                         alpha = 0.0,
                         beta = 1.0,
                         norm_type = NORM_MINMAX,
                         dtype = None,
                         mask = None)
    _, _, _, maxLoc = minMaxLoc(src = distNorm,
                                mask = None)
    return maxLoc

def euclideanDistanceTransformNorm255(binImg: MatLike,
                                      distanceType: int = DIST_L2,
                                      maskSize: int = DIST_MASK_5) -> tuple:
    """
    Calculates euclidean distance between each non-zero pixel and nearest
    zero pixel in a binary image. Returns location of non-zero pixel with
    largest distance to nearest zero pixel.
    Pixel values normalized between [0, 255].

    Parameters
    ----------
    binImg: MatLike
        binary image

    distanceType: int
        distance type used to calculate distance (default: cv2.DIST_L2)

    maskSize: int
        mask size used to calculate distance (default: cv2.DIST_MASK_5)

    Returns
    -------
    maxLoc: tuple
        location of non-zero pixel with largest distance to nearest zero
        pixel
    """
    dist = distanceTransform(src = binImg,
                             distanceType = distanceType,
                             maskSize = maskSize,
                             dst = None,
                             dstType = None)
    distNorm = normalize(src = dist,
                         dst = None,
                         alpha = 0.0,
                         beta = 255.0,
                         norm_type = NORM_MINMAX,
                         dtype = None,
                         mask = None)
    _, _, _, maxLoc = minMaxLoc(src = distNorm,
                                mask = None)
    return maxLoc