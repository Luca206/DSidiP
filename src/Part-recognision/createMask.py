from cv2 import cvtColor, GaussianBlur, inRange, \
                COLOR_BGR2HSV
from cv2.typing import MatLike
from numpy import asarray
from numpy.typing import NDArray

def create_mask_bgr2_hsv(img: MatLike,
                         lower_b: NDArray,
                         upper_b: NDArray,
                         lower_b_2: NDArray = asarray(None),
                         upper_b_2: NDArray = asarray(None)) -> MatLike:
    """
    Create mask (binary image) from BGR image within the specified HSV boundary.

    Parameters
    ----------
    img: MatLike
        BGR input image

    lower_b: NDArray
        lower HSV boundary

    upper_b: NDArray
        upper HSV boundary

    lower_b_2: NDArray
        optional, secondary lower HSV boundary (default: None) \n
        (required, if boundary wraps around HSV space)

    upper_b_2: NDArray
        optional, secondary upper HSV boundary (default: None) \n
        (required, if boundary wraps around HSV space)

    Returns
    -------
    mask: MatLike
        binary image, where pixels within the specified boundary have the value 255, else 0
    """
    img = GaussianBlur(img, (5, 5), 0)
    hsv = cvtColor(img, COLOR_BGR2HSV)
    if (lower_b_2.all() != None) and (upper_b_2.all() != None):
        mask1 = inRange(hsv, lower_b, upper_b)
        mask2 = inRange(hsv, lower_b_2, upper_b_2)
        mask = mask1 + mask2
    else:
        mask = inRange(hsv, lower_b, upper_b)
    return mask