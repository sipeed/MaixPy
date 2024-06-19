from maix import image
import math

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
                if self.__img is None:
                    raise Exception(f"load image {path} failed")

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

def RGB2XYZ(r, g, b):
    x = 0.412453 * r + 0.357580 * g + 0.180423 * b
    y = 0.212671 * r + 0.715160 * g + 0.072169 * b
    z = 0.019334 * r + 0.119193 * g + 0.950227 * b
    return x, y, z

def XYZ2Lab(x, y, z):
    Xn = 1.0
    Yn = 1.0
    Zn = 1.0
    param_13 = 1.0 / 3.0
    param_16116 = 16.0 / 116.0

    x /=  255 * Xn
    y /= 255 * Yn
    z /= 255 * Zn
    if y > 0.008856:
        fy = pow(y, param_13)
        l = 116.0 * fy - 16.0
    else:
        fy = 7.787 * y + param_16116
        l = 903.3 * fy

    if l < 0:
        l = 0.0

    if x>0.008856:
        fx = pow(x,param_13)
    else:
        fx = 7.787 * x + param_16116

    if z>0.008856:
        fz = pow(z,param_13)
    else:
        fz = 7.787 * z + param_16116

    a = 500.0*(fx-fy)
    b = 200.0*(fy-fz)

    return (round(l,2), round(a,2), round(b,2))

__xyz_table = [
    0.000000,  0.030353,  0.060705,  0.091058,  0.121411,  0.151763,  0.182116,  0.212469,
    0.242822,  0.273174,  0.303527,  0.334654,  0.367651,  0.402472,  0.439144,  0.477695,
    0.518152,  0.560539,  0.604883,  0.651209,  0.699541,  0.749903,  0.802319,  0.856813,
    0.913406,  0.972122,  1.032982,  1.096009,  1.161225,  1.228649,  1.298303,  1.370208,
    1.444384,  1.520851,  1.599629,  1.680738,  1.764195,  1.850022,  1.938236,  2.028856,
    2.121901,  2.217388,  2.315337,  2.415763,  2.518686,  2.624122,  2.732089,  2.842604,
    2.955683,  3.071344,  3.189603,  3.310477,  3.433981,  3.560131,  3.688945,  3.820437,
    3.954624,  4.091520,  4.231141,  4.373503,  4.518620,  4.666509,  4.817182,  4.970657,
    5.126946,  5.286065,  5.448028,  5.612849,  5.780543,  5.951124,  6.124605,  6.301002,
    6.480327,  6.662594,  6.847817,  7.036010,  7.227185,  7.421357,  7.618538,  7.818742,
    8.021982,  8.228271,  8.437621,  8.650046,  8.865559,  9.084171,  9.305896,  9.530747,
    9.758735,  9.989873, 10.224173, 10.461648, 10.702310, 10.946171, 11.193243, 11.443537,
    11.697067, 11.953843, 12.213877, 12.477182, 12.743768, 13.013648, 13.286832, 13.563333,
    13.843162, 14.126329, 14.412847, 14.702727, 14.995979, 15.292615, 15.592646, 15.896084,
    16.202938, 16.513219, 16.826940, 17.144110, 17.464740, 17.788842, 18.116424, 18.447499,
    18.782077, 19.120168, 19.461783, 19.806932, 20.155625, 20.507874, 20.863687, 21.223076,
    21.586050, 21.952620, 22.322796, 22.696587, 23.074005, 23.455058, 23.839757, 24.228112,
    24.620133, 25.015828, 25.415209, 25.818285, 26.225066, 26.635560, 27.049779, 27.467731,
    27.889426, 28.314874, 28.744084, 29.177065, 29.613827, 30.054379, 30.498731, 30.946892,
    31.398871, 31.854678, 32.314321, 32.777810, 33.245154, 33.716362, 34.191442, 34.670406,
    35.153260, 35.640014, 36.130678, 36.625260, 37.123768, 37.626212, 38.132601, 38.642943,
    39.157248, 39.675523, 40.197778, 40.724021, 41.254261, 41.788507, 42.326767, 42.869050,
    43.415364, 43.965717, 44.520119, 45.078578, 45.641102, 46.207700, 46.778380, 47.353150,
    47.932018, 48.514994, 49.102085, 49.693300, 50.288646, 50.888132, 51.491767, 52.099557,
    52.711513, 53.327640, 53.947949, 54.572446, 55.201140, 55.834039, 56.471151, 57.112483,
    57.758044, 58.407842, 59.061884, 59.720179, 60.382734, 61.049557, 61.720656, 62.396039,
    63.075714, 63.759687, 64.447968, 65.140564, 65.837482, 66.538730, 67.244316, 67.954247,
    68.668531, 69.387176, 70.110189, 70.837578, 71.569350, 72.305513, 73.046074, 73.791041,
    74.540421, 75.294222, 76.052450, 76.815115, 77.582222, 78.353779, 79.129794, 79.910274,
    80.695226, 81.484657, 82.278575, 83.076988, 83.879901, 84.687323, 85.499261, 86.315721,
    87.136712, 87.962240, 88.792312, 89.626935, 90.466117, 91.309865, 92.158186, 93.011086,
    93.868573, 94.730654, 95.597335, 96.468625, 97.344529, 98.225055, 99.110210, 100.000000
]

def rgb_to_lab(rgb_tuple):
    r = int(rgb_tuple[0])
    g = int(rgb_tuple[1])
    b = int(rgb_tuple[2])

    r_lin = __xyz_table[r]
    g_lin = __xyz_table[g]
    b_lin = __xyz_table[b]

    x = ((r_lin * 0.4124) + (g_lin * 0.3576) + (b_lin * 0.1805)) * (1.0 / 95.047)
    y = ((r_lin * 0.2126) + (g_lin * 0.7152) + (b_lin * 0.0722)) * (1.0 / 100.000)
    z = ((r_lin * 0.0193) + (g_lin * 0.1192) + (b_lin * 0.9505)) * (1.0 / 108.883)

    if x > 0.008856:
        x = x ** (1 / 3)
    else:
        x = (x * 7.787037) + 0.137931

    if y > 0.008856:
        y = y ** (1 / 3)
    else:
        y = (y * 7.787037) + 0.137931

    if z > 0.008856:
        z = z ** (1 / 3)
    else:
        z = (z * 7.787037) + 0.137931

    l = max(min(math.floor(116 * y) - 16, 100), 0)
    a = max(min(math.floor(500 * (x-y)), 127), -128)
    b = max(min(math.floor(200 * (y-z)), 127), -128)

    return (l,a,b)

def lab_to_rgb(lab_tuple):
    l = int(lab_tuple[0])
    a = int(lab_tuple[1])
    b = int(lab_tuple[2])

    x = ((l + 16) * 0.008621) + (a * 0.002)
    y = ((l + 16) * 0.008621)
    z = ((l + 16) * 0.008621) - (b * 0.005)

    if x > 0.206897:
        x = x * x * x * 95.047
    else:
        x = (((0.128419 * x) - 0.017713)) * 95.047

    if y > 0.206897:
        y = y * y * y * 100.000
    else:
        y = ((0.128419 * y) - 0.017713) * 100.000

    if z > 0.206897:
        z = z * z * z * 108.883
    else:
        z = ((0.128419 * z) - 0.017713) * 108.883

    r_lin = ((x * +3.2406) + (y * -1.5372) + (z * -0.4986)) / 100.0
    g_lin = ((x * -0.9689) + (y * +1.8758) + (z * +0.0415)) / 100.0
    b_lin = ((x * +0.0557) + (y * -0.2040) + (z * +1.0570)) / 100.0

    if r_lin > 0.0031308:
        r_lin = 1.055 * (r_lin ** 0.416666) - 0.055
    else:
        r_lin = r_lin * 12.92

    if g_lin > 0.0031308:
        g_lin = 1.055 * (g_lin ** 0.416666) - 0.055
    else:
        g_lin = g_lin * 12.92

    if b_lin > 0.0031308:
        b_lin = 1.055 * (b_lin ** 0.416666) - 0.055
    else:
        r_lin = r_lin * 12.92

    r = max(min(math.floor(r_lin * 255), 255), 0)
    g = max(min(math.floor(g_lin * 255), 255), 0)
    b = max(min(math.floor(b_lin * 255), 255), 0)

    return (r,g,b)

def rgb_to_grayscale(rgb_tuple):
    r = rgb_tuple[0]
    g = rgb_tuple[1]
    b = rgb_tuple[2]
    y = ((((r) * 38) + ((g) * 75) + ((b) * 15)) >> 7)
    return y

def grayscale_to_rgb(g_value):
    return (g_value, g_value, g_value)

def load_decriptor(path):
    raise ValueError('This operation is not supported')

def save_descriptor(path, descriptor):
    raise ValueError('This operation is not supported')

def match_descriptor(descritor0, descriptor1, threshold=70, filter_outliers=False):
    raise ValueError('This operation is not supported')