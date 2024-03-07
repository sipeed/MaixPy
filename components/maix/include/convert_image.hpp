#pragma once

#include "maix_image.hpp"
#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"

namespace py = pybind11;

namespace maix::image
{
    /**
     * OpenCV Mat(numpy array object) to Image object
     * @param array numpy array object, must be a 3-dim or 2-dim continuous array with shape hwc or hw
     * @return Image object
     * @maixpy maix.image.cv2image
     */
    image::Image *cv2image(py::array_t<uint8_t, py::array::c_style> array, bool bgr = true, bool copy = true)
    {
        py::buffer_info info = array.request();
        cv::Mat mat;
        if (info.ndim != 3 && info.ndim != 2)
            throw std::runtime_error("Number of dimensions must be 3");
        if (info.format != py::format_descriptor<uint8_t>::format())
            throw std::runtime_error("Unsupported buffer format!");
        if(info.ndim == 3)
        {
            log::debug("ndim: %ld, shape: %ld %ld %ld\n", info.ndim, info.shape[0], info.shape[1], info.shape[2]);
            if (info.shape[2] != 3 && info.shape[2] != 4)
                throw std::runtime_error("Number of channels must be 3 or 4");
            mat = cv::Mat(info.shape[0], info.shape[1], CV_8UC(info.shape[2]), info.ptr);
        }
        else
        {
            log::debug("ndim: %ld, shape: %ld %ld \n", info.ndim, info.shape[0], info.shape[1]);
            mat = cv::Mat(info.shape[0], info.shape[1], CV_8UC1, info.ptr);
        }
        image::Format fmt = image::Format::FMT_RGB888;
        if (mat.channels() == 1)
            fmt = image::Format::FMT_GRAYSCALE;
        else if (mat.channels() == 3)
        {
            if (bgr)
                fmt = image::Format::FMT_BGR888;
            else
                fmt = image::Format::FMT_RGB888;
        }
        else if (mat.channels() == 4)
        {
            if (bgr)
                fmt = image::Format::FMT_BGRA8888;
            else
                fmt = image::Format::FMT_RGBA8888;
        }
        else
            throw std::runtime_error("not support channels");
        image::Image *img;
        if (copy)
        {
            img = new image::Image(mat.cols, mat.rows, fmt);
            memcpy(img->data(), mat.data, mat.cols * mat.rows * image::fmt_size[fmt]);
        }
        else
        {
            img = new image::Image(mat.cols, mat.rows, fmt, mat.data);
        }
        return img;
    }

    /**
     * Image object to OpenCV Mat(numpy array object)
     * @param img Image object
     * @return numpy array object
     * @maixpy maix.image.image2cv
     */
    py::array_t<uint8_t, py::array::c_style> image2cv(image::Image *img, bool bgr = true, bool copy = true)
    {
        return py::array_t<uint8_t, py::array::c_style>({img->height(), img->width(), (int)image::fmt_size[img->format()]}, (const unsigned char*)img->data(), py::cast(img));
    }
} // namespace maix::image
