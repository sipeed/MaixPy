
#include "maix_basic.hpp"
#include "main.h"
#include <pybind11/embed.h> // everything needed for embedding


namespace py = pybind11;

using namespace maix;

int _main(int argc, char* argv[])
{
    py::scoped_interpreter guard{};
    // FIXME: run occurs core dump
    py::exec(R"(
        print("python start")

        from _maix import app

        print("Hello MaixPy")
        print(maix.app.app_id())
    )");

    return 0;
}

int main(int argc, char* argv[])
{
    // Catch SIGINT signal(e.g. Ctrl + C), and set exit flag to true.
    signal(SIGINT, [](int sig){ app::set_exit_flag(true); });

    // Use CATCH_EXCEPTION_RUN_RETURN to catch exception,
    // if we don't catch exception, when program throw exception, the objects will not be destructed.
    // So we catch exception here to let resources be released(call objects' destructor) before exit.
    CATCH_EXCEPTION_RUN_RETURN(_main, -1, argc, argv);
}
