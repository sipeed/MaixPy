from maix import image

SEARCH_EX       = 0
SEARCH_DS       = 1

EDGE_CANNY      = 0
EDGE_SIMPLE     = 1

CORNER_FAST     = 0
CORNER_AGAST    = 1

TAG16H5         = 0
TAG25H7         = 1
TAG25H9         = 2
TAG36H10        = 3
TAG36H11        = 4
ARTOOLKIT       = 5
EAN2            = 0
EAN5            = 1
EAN8            = 2
UPCE            = 3
ISBN10          = 4
UPCA            = 5
EAN13           = 6
ISBN13          = 7
I25             = 8
DATABAR         = 9
DATABAR_EXP     = 10
CODABAR         = 11
CODE39          = 12
PDF417          = 13
CODE93          = 14
CODE128         = 15

class Histogram:
    def __init__(self):
        raise ValueError('This operation is not supported')

    def bins(self):
        raise ValueError('This operation is not supported')

    def l_bins(self):
        raise ValueError('This operation is not supported')

    def a_bins(self):
        raise ValueError('This operation is not supported')

    def b_bins(self):
        raise ValueError('This operation is not supported')

    def get_percentile(self, percentile):
        raise ValueError('This operation is not supported')

    def get_threhsold(self):
        raise ValueError('This operation is not supported')

    def get_statistics(self):
        raise ValueError('This operation is not supported')

class Statistics:
    def __init__(self):
        raise ValueError('This operation is not supported')

    def mean(self):
        raise ValueError('This operation is not supported')

    def median(self):
        raise ValueError('This operation is not supported')

    def mode(self):
        raise ValueError('This operation is not supported')

    def stdev(self):
        raise ValueError('This operation is not supported')

    def min(self):
        raise ValueError('This operation is not supported')

    def max(self):
        raise ValueError('This operation is not supported')

    def lq(self):
        raise ValueError('This operation is not supported')

    def uq(self):
        raise ValueError('This operation is not supported')

    def l_mean(self):
        raise ValueError('This operation is not supported')

    def l_median(self):
        raise ValueError('This operation is not supported')

    def l_mode(self):
        raise ValueError('This operation is not supported')

    def l_stdev(self):
        raise ValueError('This operation is not supported')

    def l_min(self):
        raise ValueError('This operation is not supported')

    def l_max(self):
        raise ValueError('This operation is not supported')

    def l_lq(self):
        raise ValueError('This operation is not supported')

    def l_uq(self):
        raise ValueError('This operation is not supported')

    def a_mean(self):
        raise ValueError('This operation is not supported')

    def a_median(self):
        raise ValueError('This operation is not supported')

    def a_mode(self):
        raise ValueError('This operation is not supported')

    def a_stdev(self):
        raise ValueError('This operation is not supported')

    def a_min(self):
        raise ValueError('This operation is not supported')

    def a_max(self):
        raise ValueError('This operation is not supported')

    def a_lq(self):
        raise ValueError('This operation is not supported')

    def a_uq(self):
        raise ValueError('This operation is not supported')

    def b_mean(self):
        raise ValueError('This operation is not supported')

    def b_median(self):
        raise ValueError('This operation is not supported')

    def b_mode(self):
        raise ValueError('This operation is not supported')

    def b_stdev(self):
        raise ValueError('This operation is not supported')

    def b_min(self):
        raise ValueError('This operation is not supported')

    def b_max(self):
        raise ValueError('This operation is not supported')

    def b_lq(self):
        raise ValueError('This operation is not supported')

    def b_uq(self):
        raise ValueError('This operation is not supported')

class Blob:
    def __init__(self):
        raise ValueError('This operation is not supported')

    def rect(self):
        raise ValueError('This operation is not supported')

    def x(self):
        raise ValueError('This operation is not supported')

    def y(self):
        raise ValueError('This operation is not supported')

    def w(self):
        raise ValueError('This operation is not supported')

    def h(self):
        raise ValueError('This operation is not supported')

    def pixels(self):
        raise ValueError('This operation is not supported')

    def cx(self):
        raise ValueError('This operation is not supported')

    def cy(self):
        raise ValueError('This operation is not supported')

    def rotation(self):
        raise ValueError('This operation is not supported')

    def code(self):
        raise ValueError('This operation is not supported')

    def count(self):
        raise ValueError('This operation is not supported')

    def area(self):
        raise ValueError('This operation is not supported')

    def density(self):
        raise ValueError('This operation is not supported')

class Line:
    def __init__(self):
        raise ValueError('This operation is not supported')

    def line(self):
        raise ValueError('This operation is not supported')

    def x1(self):
        raise ValueError('This operation is not supported')

    def y1(self):
        raise ValueError('This operation is not supported')

    def x2(self):
        raise ValueError('This operation is not supported')

    def y2(self):
        raise ValueError('This operation is not supported')

    def length(self):
        raise ValueError('This operation is not supported')

    def magnitude(self):
        raise ValueError('This operation is not supported')

    def theta(self):
        raise ValueError('This operation is not supported')

    def rho(self):
        raise ValueError('This operation is not supported')


class Circle:
    def __init__(self):
        raise ValueError('This operation is not supported')

    def x(self):
        raise ValueError('This operation is not supported')

    def y(self):
        raise ValueError('This operation is not supported')

    def r(self):
        raise ValueError('This operation is not supported')

    def magnitude(self):
        raise ValueError('This operation is not supported')


class Rect:
    def __init__(self):
        raise ValueError('This operation is not supported')

    def corners(self):
        raise ValueError('This operation is not supported')

    def rect(self):
        raise ValueError('This operation is not supported')

    def x(self):
        raise ValueError('This operation is not supported')

    def y(self):
        raise ValueError('This operation is not supported')

    def w(self):
        raise ValueError('This operation is not supported')

    def h(self):
        raise ValueError('This operation is not supported')

    def magnitude(self):
        raise ValueError('This operation is not supported')


class QRCode:
    def __init__(self):
        raise ValueError('This operation is not supported')

    def corners(self):
        raise ValueError('This operation is not supported')

    def rect(self):
        raise ValueError('This operation is not supported')

    def x(self):
        raise ValueError('This operation is not supported')

    def y(self):
        raise ValueError('This operation is not supported')

    def w(self):
        raise ValueError('This operation is not supported')

    def h(self):
        raise ValueError('This operation is not supported')

    def payload(self):
        raise ValueError('This operation is not supported')

    def version(self):
        raise ValueError('This operation is not supported')

    def ecc_level(self):
        raise ValueError('This operation is not supported')

    def mask(self):
        raise ValueError('This operation is not supported')

    def data_type(self):
        raise ValueError('This operation is not supported')

    def eci(self):
        raise ValueError('This operation is not supported')

    def is_numeric(self):
        raise ValueError('This operation is not supported')

    def is_alphanumeric(self):
        raise ValueError('This operation is not supported')

    def is_binary(self):
        raise ValueError('This operation is not supported')

    def is_kanji(self):
        raise ValueError('This operation is not supported')


class AprilTag:
    def __init__(self):
        raise ValueError('This operation is not supported')

    def corners(self):
        raise ValueError('This operation is not supported')

    def rect(self):
        raise ValueError('This operation is not supported')

    def x(self):
        raise ValueError('This operation is not supported')

    def y(self):
        raise ValueError('This operation is not supported')

    def w(self):
        raise ValueError('This operation is not supported')

    def h(self):
        raise ValueError('This operation is not supported')

    def id(self):
        raise ValueError('This operation is not supported')

    def family(self):
        raise ValueError('This operation is not supported')

    def cx(self):
        raise ValueError('This operation is not supported')

    def cy(self):
        raise ValueError('This operation is not supported')

    def rotation(self):
        raise ValueError('This operation is not supported')

    def decision_margin(self):
        raise ValueError('This operation is not supported')

    def hamming(self):
        raise ValueError('This operation is not supported')

    def goodness(self):
        raise ValueError('This operation is not supported')

    def x_translation(self):
        raise ValueError('This operation is not supported')

    def y_translation(self):
        raise ValueError('This operation is not supported')

    def z_translation(self):
        raise ValueError('This operation is not supported')

    def x_rotation(self):
        raise ValueError('This operation is not supported')

    def y_rotation(self):
        raise ValueError('This operation is not supported')

    def z_rotation(self):
        raise ValueError('This operation is not supported')

class DataMatrix:
    def __init__(self):
        raise ValueError('This operation is not supported')

    def corners(self):
        raise ValueError('This operation is not supported')

    def rect(self):
        raise ValueError('This operation is not supported')

    def x(self):
        raise ValueError('This operation is not supported')

    def y(self):
        raise ValueError('This operation is not supported')

    def w(self):
        raise ValueError('This operation is not supported')

    def h(self):
        raise ValueError('This operation is not supported')

    def payload(self):
        raise ValueError('This operation is not supported')

    def rotation(self):
        raise ValueError('This operation is not supported')

    def rows(self):
        raise ValueError('This operation is not supported')

    def columns(self):
        raise ValueError('This operation is not supported')

    def capacity(self):
        raise ValueError('This operation is not supported')

    def padding(self):
        raise ValueError('This operation is not supported')

class BarCode:
    def __init__(self):
        raise ValueError('This operation is not supported')

    def corners(self):
        raise ValueError('This operation is not supported')

    def rect(self):
        raise ValueError('This operation is not supported')

    def x(self):
        raise ValueError('This operation is not supported')

    def y(self):
        raise ValueError('This operation is not supported')

    def w(self):
        raise ValueError('This operation is not supported')

    def h(self):
        raise ValueError('This operation is not supported')

    def payload(self):
        raise ValueError('This operation is not supported')

    def type(self):
        raise ValueError('This operation is not supported')

    def rotation(self):
        raise ValueError('This operation is not supported')

    def quality(self):
        raise ValueError('This operation is not supported')

class Displacement:
    def __init__(self):
        raise ValueError('This operation is not supported')

    def x_translation(self):
        raise ValueError('This operation is not supported')

    def y_translation(self):
        raise ValueError('This operation is not supported')

    def rotation(self):
        raise ValueError('This operation is not supported')

    def scale(self):
        raise ValueError('This operation is not supported')

    def response(self):
        raise ValueError('This operation is not supported')

class Image:
    def __init__(self, path=None, copy_to_fb=False, width=640, height=480, do_nothing = False):
        if do_nothing:
            self.__img = None
        else:
            if path is None:
                self.__img = image.Image(width, height)
            else:
                self.__img = image.load(path)

    def get_priv_img(self):
        return self.__img

    def set_priv_img(self, new_image):
        self.__img = new_image

    def width(self):
        return self.__img.width()

    def height(self):
        return self.__img.height()

    def format(self):
        format_int = 0
        if self.__img.format() == image.Format.FMT_GRAYSCALE:
            return 1
        elif self.__img.format() == image.Format.FMT_RGB565:
            return 2
        elif self.__img.format() == image.Format.FMT_RGB888:
            return 4
        elif self.__img.format() == image.Format.FMT_YVU420SP:
            return 5
        else:
            raise ValueError('Unknowed format')

    def size(self):
        return self.__img.data_size()

    def get_pixel(self, x, y, rgbtuple = False):
        return self.__img.get_pixel(x, y, rgbtuple)

    def set_pixel(self, x, y, pixel):
        self.__img.set_pixel(x, y, pixel)

    def mean_pool(self, x_div, y_div):
        img = self.__img.mean_pool(x_div, y_div, copy = False)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)
        return img_v1

    def mean_pooled(self, x_div, y_div):
        return self.mean_pool(x_div, y_div)

    def midpoint_pool(self, x_div, y_div, bias=0.5):
        img = self.__img.midpoint_pool(x_div, y_div, bias, copy = False)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)
        return img_v1

    def midpoint_pooled(self, x_div, y_div, bias=0.5):
        return self.midpoint_pooled(x_div, y_div, bias)

    def to_grayscale(self, copy=False):
        img = self.__img.to_format(image.Format.FMT_GRAYSCALE)
        if copy:
            img_v1 = Image(do_nothing=True)
            img_v1.set_priv_img(img)
            return img_v1
        else:
            self.__img = img
            return self

    def to_rgb565(self, copy=False):
        raise ValueError('This operation is not supported')

    def to_rainbow(self, copy=False):
        raise ValueError('This operation is not supported')

    def compress(self, quality=50):
        img = self.__img.compress(quality)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)
        return img_v1

    def compress_for_ide(self, quality=50):
        raise ValueError('This operation is not supported')

    def copy(self, roi=None, copy_to_fb=False):
        img = self.__img.copy()
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)
        return img_v1

    def save(self, path, roi=None, quality=50):
        img = self.__img.save(path, quality)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)
        return img_v1

    def clear(self):
        self.__img.clear()

    def draw_line(self, x0, y0, x1, y1, color, thickness=1):
        img_color = None
        if isinstance(color, tuple) or isinstance(color, list) and len(color) > 2:
            img_color = image.Color.from_rgb(color[0], color[1], color[2])
        elif isinstance(color, int):
            img_color = image.Color.from_rgb(color, color, color)

        self.__img.draw_line(x0, y0, x1, y1, img_color, thickness)
        return self

    def draw_rectangle(self, x, y, w, h, color, thickness=1, fill=False):
        img_color = None
        if isinstance(color, tuple) or isinstance(color, list) and len(color) > 2:
            img_color = image.Color.from_rgb(color[0], color[1], color[2])
        elif isinstance(color, int):
            img_color = image.Color.from_rgb(color, color, color)

        if fill:
            self.__img.draw_rect(x, y, w, h, img_color, -1)
        else:
            self.__img.draw_rect(x, y, w, h, img_color, thickness)

    def draw_ellipse(self, cx, cy, rx, ry, rotation, color, thickness=1, fill=False):
        img_color = None
        if isinstance(color, tuple) or isinstance(color, list) and len(color) > 2:
            img_color = image.Color.from_rgb(color[0], color[1], color[2])
        elif isinstance(color, int):
            img_color = image.Color.from_rgb(color, color, color)

        if fill:
            self.__img.draw_ellipse(cx, cy, rx, ry, rotation, 0, 360, img_color, thickness=-1)
        else:
            self.__img.draw_ellipse(cx, cy, rx, ry, rotation, 0, 360, img_color, thickness=thickness)

    def draw_circle(self, x, y, radius, color, thickness=1, fill=False):
        raise ValueError('This operation is not supported')

    def draw_string(self, x, y, text, color, scale=1, x_spacing=0, y_spacing=0, mono_space=True):
        raise ValueError('This operation is not supported')

    def draw_cross(self, x, y, color, size=5, thickness=1):
        raise ValueError('This operation is not supported')

    def draw_arrow(self, x0, y0, x1, y1, color, thickness=1):
        raise ValueError('This operation is not supported')

    def draw_image(self, image, x, y, x_scale=1.0, y_scale=1.0, mask=None, alpha=256):
        raise ValueError('This operation is not supported')

    def draw_keypoints(self, keypoints, color, size=10, thickness=1, fill=False):
        raise ValueError('This operation is not supported')

    def flood_fill(self, x, y, seed_threshold=0.05, floating_threshold=0.05, color=(255,255,255), invert=False, clear_background=False, mask=None):
        raise ValueError('This operation is not supported')

    def binary(self, thresholds, invert=False, zero=False, mask=None):
        raise ValueError('This operation is not supported')

    def invert(self):
        raise ValueError('This operation is not supported')

    def b_and(self, image, mask=None):
        raise ValueError('This operation is not supported')

    def b_nand(self, image, mask=None):
        raise ValueError('This operation is not supported')

    def b_or(self, image, mask=None):
        raise ValueError('This operation is not supported')

    def b_nor(self, image, mask=None):
        raise ValueError('This operation is not supported')

    def b_xor(self, image, mask=None):
        raise ValueError('This operation is not supported')

    def b_xnor(self, image, mask=None):
        raise ValueError('This operation is not supported')

    def erode(self, size, threshold, mask=None):
        raise ValueError('This operation is not supported')

    def dilate(self, size, threshold, mask=None):
        raise ValueError('This operation is not supported')

    def open(self, size, threshold, mask=None):
        raise ValueError('This operation is not supported')

    def close(self, size, threshold, mask=None):
        raise ValueError('This operation is not supported')

    def top_hat(self, size, threshold, mask=None):
        raise ValueError('This operation is not supported')

    def black_hat(self, size, threshold, mask=None):
        raise ValueError('This operation is not supported')

    def negate(self):
        raise ValueError('This operation is not supported')

    def replace(self, image, hmirror=False, vflip=False, mask=None):
        raise ValueError('This operation is not supported')

    def add(self, image, mask=None):
        raise ValueError('This operation is not supported')

    def sub(self, image, reverse=False, mask=None):
        raise ValueError('This operation is not supported')

    def mul(self, image, invert=False, mask=None):
        raise ValueError('This operation is not supported')

    def div(self, image, invert=False, mask=None):
        raise ValueError('This operation is not supported')

    def min(self, image, mask=None):
        raise ValueError('This operation is not supported')

    def max(self, image, mask=None):
        raise ValueError('This operation is not supported')

    def difference(self, image, mask=None):
        raise ValueError('This operation is not supported')

    def blend(self, image, alpha=128, mask=None):
        raise ValueError('This operation is not supported')

    def histeq(self, adaptive=False, clip_limit=-1, mask=None):
        raise ValueError('This operation is not supported')

    def mean(self, size, threshold=False, offset=0, invert=False, mask=None):
        raise ValueError('This operation is not supported')

    def mode(self, size, threshold=False, offset=0, invert=False, mask=None):
        raise ValueError('This operation is not supported')

    def midpoint(self, size, bias=0.5, threshold=False, offset=0, invert=False, mask=None):
        raise ValueError('This operation is not supported')

    def morph(self, size, kernel, mul=-1, add=0):
        raise ValueError('This operation is not supported')

    def gaussian(self, size, unsharp=False, mul=-1, add=0, threshold=False, offset=0, invert=False, mask=None):
        raise ValueError('This operation is not supported')

    def laplacian(self, size, sharpen=False, mul=-1, add=0, threshold=False, offset=0, invert=False, mask=None):
        raise ValueError('This operation is not supported')

    def bilateral(self, size, color_sigma=0.1, space_sigma=1, threshold=False, offset=0, invert=False, mask=None):
        raise ValueError('This operation is not supported')

    def cartoon(self, size, seed_threshold=0.05, floating_threshold=0.05, mask=None):
        raise ValueError('This operation is not supported')

    def remove_shadows(self, image):
        raise ValueError('This operation is not supported')

    def chrominvar(self):
        raise ValueError('This operation is not supported')

    def illuminvar(self):
        raise ValueError('This operation is not supported')

    def linpolar(self, reverse=False):
        raise ValueError('This operation is not supported')

    def logpolar(self, reverse=False):
        raise ValueError('This operation is not supported')

    def lens_corr(self, strength=1.8, zoom=1.0):
        raise ValueError('This operation is not supported')

    def rotation_corr(self, x_rotation=0.0, y_rotation=0.0, z_rotation=0.0, x_translation=0.0, y_translation=0.0, zoom=1.0, fov=60.0, corners=None):
        raise ValueError('This operation is not supported')

    def get_similarity(self, image):
        raise ValueError('This operation is not supported')

    def get_histogram(self, thresholds, invert=False, roi=None, bins=None, l_bins=None, a_bins=None, b_bins=None):
        raise ValueError('This operation is not supported')

    def get_statistics(self, thresholds, invert=False, roi=None, bins=None, l_bins=None, a_bins=None, b_bins=None):
        raise ValueError('This operation is not supported')

    def get_regression(self, thresholds, invert=False, roi=None, x_stride=2, y_stride=1, area_threshold=10, pixels_threshold=10, robust=False):
        raise ValueError('This operation is not supported')

    def find_blobs(self, thresholds, invert=False, roi=None, x_stride=2, y_stride=1, area_threshold=10, pixels_threshold=10, merge=False, margin=0, threshold_cb=None, merge_cb=None):
        raise ValueError('This operation is not supported')

    def find_lines(self, roi=None, x_stride=2, y_stride=1, threshold=1000, theta_margin=25, rho_margin=25):
        raise ValueError('This operation is not supported')

    def find_line_segments(self, roi=None, merge_distance=0, max_theta_difference=15):
        raise ValueError('This operation is not supported')

    def find_circles(self, roi=None, x_stride=2, y_stride=1, threshold=2000, x_margin=10, y_margin=10, r_margin=10):
        raise ValueError('This operation is not supported')

    def find_rects(self, roi=None, threshold=10000):
        raise ValueError('This operation is not supported')

    def find_qrcodes(self, roi=None):
        raise ValueError('This operation is not supported')

    def find_barcodes(self, roi=None):
        raise ValueError('This operation is not supported')

    def find_number(self, roi=None):
        raise ValueError('This operation is not supported')

    def classify_object(self, roi=None):
        raise ValueError('This operation is not supported')

    def find_features(self, cascade, threshold=0.5, scale=1.5, roi=None):
        raise ValueError('This operation is not supported')

    def find_eye(self, roi=None):
        raise ValueError('This operation is not supported')

    def find_lbp(self, roi=None):
        raise ValueError('This operation is not supported')

    def find_keypoints(self, roi=None, threshold=20, normalized=False, scale_factor=1.5, max_keypoints=100, corner_detector=CORNER_AGAST):
        raise ValueError('This operation is not supported')

    def find_edges(self, edge_type, threshold):
        raise ValueError('This operation is not supported')

def rgb_to_lab(rgb_tuple):
    raise ValueError('This operation is not supported')

def lab_to_rgb(lab_tuple):
    raise ValueError('This operation is not supported')

def rgb_to_grayscale(rgb_tuple):
    raise ValueError('This operation is not supported')

def grayscale_to_rgb(g_value):
    raise ValueError('This operation is not supported')

def load_decriptor(path):
    raise ValueError('This operation is not supported')

def save_descriptor(path, descriptor):
    raise ValueError('This operation is not supported')

def match_descriptor(descritor0, descriptor1, threshold=70, filter_outliers=False):
    raise ValueError('This operation is not supported')