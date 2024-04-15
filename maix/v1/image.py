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
        if copy is True:
            img_v1 = Image(do_nothing=True)
            img_v1.set_priv_img(img)
            return img_v1
        else:
            self.__img = img
            return self

    def to_rgb565(self, copy=False):
        raise ValueError('This operation is not supported')

    def to_rgb888(self, copy=False):
        img = self.__img.to_format(image.Format.FMT_RGB888)
        if copy is True:
            img_v1 = Image(do_nothing=True)
            img_v1.set_priv_img(img)
            return img_v1
        else:
            self.__img = img
            return self

    def to_rainbow(self, copy=False):
        raise ValueError('This operation is not supported')

    def compress(self, quality=50):
        img = self.__img.compress(quality)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)
        return img_v1

    def compress_for_ide(self, quality=50):
        raise ValueError('This operation is not supported')

    def copy(self, roi=[], copy_to_fb=False):
        img = self.__img.copy()
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)
        return img_v1

    def save(self, path, roi=[], quality=50):
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
        img_color = None
        if isinstance(color, tuple) or isinstance(color, list) and len(color) > 2:
            img_color = image.Color.from_rgb(color[0], color[1], color[2])
        elif isinstance(color, int):
            img_color = image.Color.from_rgb(color, color, color)

        if fill:
            self.__img.draw_circle(x, y, radius, img_color, thickness=-1)
        else:
            self.__img.draw_circle(x, y, radius, img_color, thickness=thickness)


    def draw_string(self, x, y, text, color, scale=1, x_spacing=0, y_spacing=0, mono_space=True):
        img_color = None
        if isinstance(color, tuple) or isinstance(color, list) and len(color) > 2:
            img_color = image.Color.from_rgb(color[0], color[1], color[2])
        elif isinstance(color, int):
            img_color = image.Color.from_rgb(color, color, color)

        self.__img.draw_string(x, y, text, img_color, scale)

    def draw_cross(self, x, y, color, size=5, thickness=1):
        img_color = None
        if isinstance(color, tuple) or isinstance(color, list) and len(color) > 2:
            img_color = image.Color.from_rgb(color[0], color[1], color[2])
        elif isinstance(color, int):
            img_color = image.Color.from_rgb(color, color, color)

        self.__img.draw_cross(x, y, img_color, size, thickness=thickness)

    def draw_arrow(self, x0, y0, x1, y1, color, thickness=1):
        img_color = None
        if isinstance(color, tuple) or isinstance(color, list) and len(color) > 2:
            img_color = image.Color.from_rgb(color[0], color[1], color[2])
        elif isinstance(color, int):
            img_color = image.Color.from_rgb(color, color, color)

        self.__img.draw_arrow(x0, y0, x1, y1, img_color, thickness=thickness)

    def draw_image(self, image, x, y, x_scale=1.0, y_scale=1.0, mask=None, alpha=256):
        img = image.get_priv_img()
        print(x, y, img.width(), img.height())
        self.__img.draw_image(x, y, img)


    def draw_keypoints(self, keypoints, color, size=10, thickness=1, fill=False):
        img_color = None
        if isinstance(color, tuple) or isinstance(color, list) and len(color) > 2:
            img_color = image.Color.from_rgb(color[0], color[1], color[2])
        elif isinstance(color, int):
            img_color = image.Color.from_rgb(color, color, color)

        if fill:
            self.__img.draw_keypoints(keypoints, img_color, size, thickness=-1)
        else:
            self.__img.draw_keypoints(keypoints, img_color, size, thickness=thickness)

    def flood_fill(self, x, y, seed_threshold=0.05, floating_threshold=0.05, color=(255,255,255), invert=False, clear_background=False, mask=None):
        img_color = None
        if isinstance(color, tuple) or isinstance(color, list) and len(color) > 2:
            img_color = image.Color.from_rgb(color[0], color[1], color[2])
        elif isinstance(color, int):
            img_color = image.Color.from_rgb(color, color, color)

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()
        self.__img.flood_fill(x, y, seed_threshold, floating_threshold, img_color, invert, clear_background, mask_img)

    def binary(self, thresholds, invert=False, zero=False, mask=None):
        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()
        self.__img.binary(thresholds, invert, zero, mask_img)

    def invert(self):
        img = self.__img.invert()
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)
        return img_v1

    def b_and(self, image, mask=None):
        other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.b_and(other_img, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def b_nand(self, image, mask=None):
        other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.b_nand(other_img, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def b_or(self, image, mask=None):
        other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.b_or(other_img, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def b_nor(self, image, mask=None):
        other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.b_nor(other_img, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def b_xor(self, image, mask=None):
        other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.b_xor(other_img, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def b_xnor(self, image, mask=None):
        other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.b_xnor(other_img, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def erode(self, size, threshold, mask=None):
        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.erode(size, threshold, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def dilate(self, size, threshold, mask=None):
        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.dilate(size, threshold, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def open(self, size, threshold, mask=None):
        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.open(size, threshold, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def close(self, size, threshold, mask=None):
        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.close(size, threshold, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def top_hat(self, size, threshold, mask=None):
        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.top_hat(size, threshold, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def black_hat(self, size, threshold, mask=None):
        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.black_hat(size, threshold, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def negate(self):
        img = self.__img.negate()
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def replace(self, image, hmirror=False, vflip=False, mask=None):
        other_img = None
        if image is not None:
            other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.replace(other_img, hmirror, vflip, mask=mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def add(self, image, mask=None):
        other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.add(other_img, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def sub(self, image, reverse=False, mask=None):
        other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.sub(other_img, reverse, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def mul(self, image, invert=False, mask=None):
        other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.mul(other_img, invert, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def div(self, image, invert=False, mask=None):
        other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.div(other_img, invert, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def min(self, image, mask=None):
        other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.min(other_img, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def max(self, image, mask=None):
        other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.max(other_img, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def difference(self, image, mask=None):
        other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.difference(other_img, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def blend(self, image, alpha=128, mask=None):
        other_img = image.get_priv_img()

        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.blend(other_img, alpha, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def histeq(self, adaptive=False, clip_limit=-1, mask=None):
        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.histeq(adaptive, clip_limit, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def mean(self, size, threshold=False, offset=0, invert=False, mask=None):
        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.mean(size, threshold, offset, invert, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def mode(self, size, threshold=False, offset=0, invert=False, mask=None):
        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.mode(size, threshold, offset, invert, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def midpoint(self, size, bias=0.5, threshold=False, offset=0, invert=False, mask=None):
        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.midpoint(size, bias, threshold, offset, invert, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def morph(self, size, kernel, mul=-1, add=0):
        img = self.__img.morph(size, kernel, mul, add)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def gaussian(self, size, unsharp=False, mul=-1, add=0, threshold=False, offset=0, invert=False, mask=None):
        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.gaussian(size, unsharp, mul, add, threshold, offset, invert, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def laplacian(self, size, sharpen=False, mul=-1, add=0, threshold=False, offset=0, invert=False, mask=None):
        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.laplacian(size, sharpen, mul, add, threshold, offset, invert, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def bilateral(self, size, color_sigma=0.1, space_sigma=1, threshold=False, offset=0, invert=False, mask=None):
        mask_img = None
        if mask is not None:
            mask_img = mask.get_priv_img()

        img = self.__img.bilateral(size, color_sigma, space_sigma, threshold, offset, invert, mask_img)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def cartoon(self, size, seed_threshold=0.05, floating_threshold=0.05, mask=None):
        raise ValueError('This operation is not supported')

    def remove_shadows(self, image):
        raise ValueError('This operation is not supported')

    def chrominvar(self):
        raise ValueError('This operation is not supported')

    def illuminvar(self):
        raise ValueError('This operation is not supported')

    def linpolar(self, reverse=False):
        img = self.__img.linpolar(reverse)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def logpolar(self, reverse=False):
        img = self.__img.logpolar(reverse)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def lens_corr(self, strength=1.8, zoom=1.0):
        img = self.__img.lens_corr(strength, zoom)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def rotation_corr(self, x_rotation=0.0, y_rotation=0.0, z_rotation=0.0, x_translation=0.0, y_translation=0.0, zoom=1.0, fov=60.0, corners=None):
        img = self.__img.rotation_corr(x_rotation, y_rotation, z_rotation, x_translation, y_translation, zoom, fov, corners)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

    def get_similarity(self, image):
        raise ValueError('This operation is not supported')

    def get_histogram(self, thresholds, invert=False, roi=[], bins=-1, l_bins=100, a_bins=256, b_bins=256):
        return self.__img.get_histogram(thresholds, invert, roi, bins, l_bins, a_bins, b_bins, None)

    def get_statistics(self, thresholds, invert=False, roi=[], bins=-1, l_bins=100, a_bins=256, b_bins=256):
        return self.__img.get_statistics(thresholds, invert, roi, bins, l_bins, a_bins, b_bins, None)

    def get_regression(self, thresholds, invert=False, roi=[], x_stride=2, y_stride=1, area_threshold=10, pixels_threshold=10, robust=False):
        return self.__img.get_regression(thresholds, invert, roi, x_stride, y_stride, area_threshold, pixels_threshold, robust)

    def find_blobs(self, thresholds, invert=False, roi=[], x_stride=2, y_stride=1, area_threshold=10, pixels_threshold=10, merge=False, margin=0, threshold_cb=None, merge_cb=None):
        return self.__img.find_blobs(thresholds, invert, roi, x_stride, y_stride, area_threshold, pixels_threshold, merge, margin)

    def find_lines(self, roi=[], x_stride=2, y_stride=1, threshold=1000, theta_margin=25, rho_margin=25):
        return self.__img.find_lines(roi, x_stride, y_stride, threshold, theta_margin, rho_margin)

    def find_line_segments(self, roi=[], merge_distance=0, max_theta_difference=15):
        return self.__img.find_line_segments(roi, merge_distance, max_theta_difference)

    def find_circles(self, roi=[], x_stride=2, y_stride=1, threshold=2000, x_margin=10, y_margin=10, r_margin=10):
        return self.__img.find_circles(roi, x_stride, y_stride, threshold, x_margin, y_margin, r_margin)

    def find_rects(self, roi=[], threshold=10000):
        return self.__img.find_rects(roi, threshold)

    def find_qrcodes(self, roi=[]):
        return self.__img.find_qrcodes(roi)

    def find_barcodes(self, roi=[]):
        return self.__img.find_barcodes(roi)

    def find_number(self, roi=[]):
        raise ValueError('This operation is not supported')

    def classify_object(self, roi=[]):
        raise ValueError('This operation is not supported')

    def find_features(self, cascade, threshold=0.5, scale=1.5, roi=[]):
        raise ValueError('This operation is not supported')

    def find_eye(self, roi=[]):
        raise ValueError('This operation is not supported')

    def find_lbp(self, roi=[]):
        raise ValueError('This operation is not supported')

    def find_keypoints(self, roi=[], threshold=20, normalized=False, scale_factor=1.5, max_keypoints=100, corner_detector=CORNER_AGAST):
        raise ValueError('This operation is not supported')

    def find_edges(self, edge_type, threshold):
        dst_type = None
        if edge_type == EDGE_SIMPLE:
            dst_type = image.EdgeDetector.EDGE_SIMPLE
        else:
            dst_type = image.EdgeDetector.EDGE_CANNY

        img = self.__img.find_edges(dst_type, [], threshold)
        img_v1 = Image(do_nothing=True)
        img_v1.set_priv_img(img)

        return img_v1

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