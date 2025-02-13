from cv2 import moments
from cv2.typing import MatLike, Moments
from numpy import array

def determine_centroid_from_contour(c: list) -> tuple:
    """
    Determine the centroid from contour by averaging over points

    Parameters
    ----------
    c: list
        contour

    Returns
    -------
    tuple
        centroid
    """
    np_c = array(c)
    return tuple(np_c.mean(axis = 0))

def determine_centroid_from_binary_image(bin_img: MatLike) -> tuple:
    """
    Determine the centroid from a binary image given by the formula:

        C_x = M_10 / M_00
        C_y = M_01 / M_00

    where:

        C_x : x coordinate
        C_y : y coordinate
          M : moments

    Parameters
    ----------
    bin_img: MatLike
        binary image

    Returns
    -------
    tuple
        centroid
    """
    m = moments(bin_img)
    return determine_centroid_from_moments(m)

def determine_centroid_from_moments(m: Moments) -> tuple:
    """
    Determine the centroid from image moments given by the formula:

        C_x = M_10 / M_00
        C_y = M_01 / M_00

    where:

        C_x : x coordinate
        C_y : y coordinate
          M : moments

    Parameters
    ----------
    m: Moments
        moments

    Returns
    -------
    tuple
        centroid
    """
    c_x = int(m["m10"] / m["m00"])
    c_y = int(m["m01"] / m["m00"])
    return c_x, c_y