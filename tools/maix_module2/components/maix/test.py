from gen_api import parse_api, parse_api_from_header
from gen_api_cpp import generate_api_cpp
import os, sys


code = '''
namespace maix
{
    /**
     * @brief Example class
     *        this class will be export to MaixPy as maix.example.Example
     * @maixpy maix.example.Example
     */
    class Example
    {
    };
}

namespace maix
{
    /**
     * @brief Example class
     *        this class will be export to MaixPy as maix.example.Example
     * @maixpy maix.example.Example
     */
    class Example
    {
    };
}

'''

test_header = sys.argv[1]

curr_dir = os.path.abspath(os.path.dirname(__file__))

res = parse_api_from_header(os.path.join(curr_dir, test_header))
import json, os

with open("test.json", "w") as f:
    f.write(json.dumps(res, indent=4))

generate_api_cpp(res, [os.path.join(curr_dir, test_header)], "test.cpp")
