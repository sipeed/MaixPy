#include "maix_kws.hpp"
#include "decoder_kws.h"
#include "ms_asr.h"
#include "ms_asr_cfg.h"

namespace maix_kws::basic
{
    void hello(const std::string &name)
    {
        maix::log::info(("hello: " + name).c_str());
    }
} // namespace maix_kws
