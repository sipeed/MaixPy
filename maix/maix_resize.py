import argparse
import sys

def main_cli():
    parser = argparse.ArgumentParser(description='Resize image')
    parser.add_argument('--input', '-i', required=True, help='input image')
    parser.add_argument('--output', '-o', required=True, help='output image')
    parser.add_argument('--width', required=True, type=int, default=-1, help='output width, -1 means auto')
    parser.add_argument('--height', required=True, type=int, default=-1, help='output height, -1 means auto')
    parser.add_argument('--fit', '-f', type=str, default='contain', help='fill|contain|cover')
    args = parser.parse_args()
    if args.width <= 0 and args.height <= 0:
        print('Error: one of width and height must be set')
        sys.exit(1)

    from maix import image
    img = image.load(args.input)
    if img is None:
        raise Exception(f"load image {args.input} failed")
    fit = {
        'fill': image.Fit.FIT_FILL,
        'contain': image.Fit.FIT_CONTAIN,
        'cover': image.Fit.FIT_COVER,
    }.get(args.fit, image.Fit.FIT_CONTAIN)
    img = img.resize(args.width, args.height, fit)
    img.save(args.output)

if __name__ == '__main__':
    main_cli()
