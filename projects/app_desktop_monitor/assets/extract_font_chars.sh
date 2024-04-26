#!/bin/bash

echo "Extracting font characters from $1"

fonttools subset --text-file=chars.txt --output-file=my_font.ttf $1


