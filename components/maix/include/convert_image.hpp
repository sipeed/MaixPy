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
     * @param bgr if set bgr, the return image will be marked as BGR888 or BGRA8888 format(only mark, not ensure return image is real BGR format), grayscale will ignore this arg.
     * @param copy if true, will alloc new buffer and copy data, else will directly use array's data buffer, default true.
     *        Use this arg carefully, when set to false, ther array MUST keep alive until we don't use the return img of this func, or will cause program crash.
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
            if (info.shape[2] != 3 && info.shape[2] != 4 && info.shape[2] != 1)
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
            img = new image::Image(mat.cols, mat.rows, fmt, mat.data, -1, false);
        }
        return img;
    }

    /**
     * Image object to OpenCV Mat(numpy array object)
     * @param img Image object, maix.image.Image type.
     * @param ensure_bgr auto convert to BGR888 or BGRA8888 if img format is not BGR or BGRA, if set to false, will not auto convert and directly use img's data, default true.
     *                   If copy is false, ensure_bgr always be false.
     * @param copy Whether alloc new image and copy data or not, if ensure_bgr and img is not bgr or bgra format, always copy,
     *        if not copy, array object will directly use img's data buffer, will faster but change array will affect img's data, default true.
     * @attention take care of ensure_bgr and copy param.
     * @return numpy array object
     * @maixpy maix.image.image2cv
     */
    py::array_t<uint8_t, py::array::c_style> image2cv(image::Image *img, bool ensure_bgr = true, bool copy = true)
    {
        if(!copy)
            ensure_bgr = false;
        // no need to convert to bgr
        if(!ensure_bgr || (!ensure_bgr && img->format() == image::FMT_GRAYSCALE) || img->format() == image::FMT_BGR888 || img->format() == image::FMT_BGRA8888)
        {
            if(!copy)
                return py::array_t<uint8_t, py::array::c_style>({img->height(), img->width(), (int)image::fmt_size[img->format()]}, (const unsigned char*)img->data(), py::cast(img));
            image::Image *new_img = new image::Image(img->width(), img->height(), img->format());
            if(!new_img)
                throw err::Exception(err::ERR_NO_MEM);
            memcpy(new_img->data(), img->data(), img->data_size());
            auto capsule = py::capsule(new_img, [](void* img_ptr) {
                delete reinterpret_cast<image::Image*>(img_ptr);
            });
            return py::array_t<uint8_t, py::array::c_style>({new_img->height(), new_img->width(), (int)image::fmt_size[img->format()]}, (const unsigned char*)new_img->data(), capsule);
        }
        // need convert to BGR
        image::Image *new_img = img->to_format(img->format() == image::FMT_RGBA8888 ? image::FMT_BGRA8888 : image::FMT_BGR888);
        auto capsule = py::capsule(new_img, [](void* img_ptr) {
            delete reinterpret_cast<image::Image*>(img_ptr);
        });
        return py::array_t<uint8_t, py::array::c_style>({new_img->height(), new_img->width(), (int)image::fmt_size[img->format()]}, (const unsigned char*)new_img->data(), capsule);
    }
} // namespace maix::image
