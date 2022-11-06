import tempfile
from typing import Generator

import numpy as np
import scipy as sp

from PIL import Image
from matplotlib.pyplot import imread
from scipy.signal.signaltools import correlate2d as c2d

import models


def compare_signatures_0(
        set_0: Generator[models.Signature, None, None],
        set_1: Generator[models.Signature, None, None]
) -> models.Compare:
    def meta_to_img(meta: dict) -> Image.Image:
        im = Image.fromarray(np.uint8(meta["img"]["data"])).convert('RGB')
        return im

    max_list = []
    for ind, s0 in enumerate(set_0):
        max_list.append(0)
        for s1 in set_1:
            max_list[ind] = max(
                max_list[ind],
                _compare_images(
                    *map(
                        meta_to_img,
                        [s0.meta, s1.meta]
                    )
                )
            )

    return models.Compare(
        version=0,
        result=sum(max_list) / len(max_list)
    )


def _compare_images(i0: Image.Image, i1: Image.Image):
    # https://stackoverflow.com/questions/1819124/image-comparison-algorithm
    def get(img: Image.Image):
        with tempfile.NamedTemporaryFile() as f:
            img.save(f, format='JPEG', quality=100)
            f.seek(0)
            data = imread(f)
            data = sp.inner(data, [299, 587, 114]) / 1000.0
            return (data - data.mean()) / data.std()

    return c2d(get(i0), get(i1), mode='same').max()