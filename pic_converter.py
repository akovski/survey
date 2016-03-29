import os
import glob
import cv2
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', required=True)
    parser.add_argument('--output', '-o', required=True)
    args = parser.parse_args()
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    for cnt, pic in enumerate(sorted(glob.glob(os.path.join(args.input, '*')))):
        print pic
        dirname, basename = os.path.split(pic)
        img = cv2.imread(pic)
        ox, oy = img.shape[:2]
        ox /= 2
        oy /= 2
        img = img[ox-350:ox+350, oy-350:oy+350]
        #cv2.imwrite(os.path.join(args.output, basename.replace('.png', '.jpg')), img)
        cv2.imwrite(os.path.join(args.output, '{}.{}.jpg'.format(cnt / 6 + 1, cnt % 6 + 1)), img)

