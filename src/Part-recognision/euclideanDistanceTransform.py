from cv2 import distanceTransform, minMaxLoc, normalize, \
                DIST_L2, DIST_MASK_5, NORM_MINMAX
from cv2.typing import MatLike

def euclidean_distance_transform(bin_img: MatLike,
                                 distance_type: int = DIST_L2,
                                 mask_size: int = DIST_MASK_5) -> tuple:
    """
    Calculates euclidean distance between each non-zero pixel and nearest
    zero pixel in a binary image. Returns location of non-zero pixel with
    largest distance to nearest zero pixel.

    Parameters
    ----------
    bin_img: MatLike
        binary image

    distance_type: int
        distance type used to calculate distance (default: cv2.DIST_L2)

    mask_size: int
        mask size used to calculate distance (default: cv2.DIST_MASK_5)

    Returns
    -------
    max_loc: tuple
        location of non-zero pixel with largest distance to nearest zero
        pixel
    """
    dist = distanceTransform(src = bin_img,
                             distanceType = distance_type,
                             maskSize = mask_size,
                             dst = None,
                             dstType = None)
    _, _, _, max_loc = minMaxLoc(src = dist,
                                mask = None)
    return max_loc

def euclidean_distance_transform_norm1(bin_img: MatLike,
                                       distance_type: int = DIST_L2,
                                       mask_size: int = DIST_MASK_5) -> tuple:
    """
    Calculates euclidean distance between each non-zero pixel and nearest
    zero pixel in a binary image. Returns location of non-zero pixel with
    largest distance to nearest zero pixel.
    Pixel values normalized between [0, 1].

    Parameters
    ----------
    bin_img: MatLike
        binary image

    distance_type: int
        distance type used to calculate distance (default: cv2.DIST_L2)

    mask_size: int
        mask size used to calculate distance (default: cv2.DIST_MASK_5)

    Returns
    -------
    max_loc: tuple
        location of non-zero pixel with largest distance to nearest zero
        pixel
    """
    dist = distanceTransform(src = bin_img,
                             distanceType = distance_type,
                             maskSize = mask_size,
                             dst = None,
                             dstType = None)
    dist_norm = normalize(src = dist,
                         dst = None,
                         alpha = 0.0,
                         beta = 1.0,
                         norm_type = NORM_MINMAX,
                         dtype = None,
                         mask = None)
    _, _, _, max_loc = minMaxLoc(src = dist_norm,
                                mask = None)
    return max_loc

def euclidean_distance_transform_norm255(bin_img: MatLike,
                                         distance_type: int = DIST_L2,
                                         mask_size: int = DIST_MASK_5) -> tuple:
    """
    Calculates euclidean distance between each non-zero pixel and nearest
    zero pixel in a binary image. Returns location of non-zero pixel with
    largest distance to nearest zero pixel.
    Pixel values normalized between [0, 255].

    Parameters
    ----------
    bin_img: MatLike
        binary image

    distance_type: int
        distance type used to calculate distance (default: cv2.DIST_L2)

    mask_size: int
        mask size used to calculate distance (default: cv2.DIST_MASK_5)

    Returns
    -------
    max_loc: tuple
        location of non-zero pixel with largest distance to nearest zero
        pixel
    """
    dist = distanceTransform(src = bin_img,
                             distanceType = distance_type,
                             maskSize = mask_size,
                             dst = None,
                             dstType = None)
    dist_norm = normalize(src = dist,
                         dst = None,
                         alpha = 0.0,
                         beta = 255.0,
                         norm_type = NORM_MINMAX,
                         dtype = None,
                         mask = None)
    _, _, _, max_loc = minMaxLoc(src = dist_norm,
                                mask = None)
    return max_loc