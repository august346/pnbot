import json
import os
import re
import subprocess
import tempfile
from typing import Generator, Iterable

import numpy as np
from PIL import Image

import models

_RUN_CMD_TEMPLATE = "ffmpeg -skip_frame nokey -i {} -vsync 2 -s 10x10 -r 30 -f image2 {}/thumbnails-%02d.jpeg"


def collect_video_data(filepath: str) -> models.Video:
    command = f'ffprobe -v quiet -print_format json -show_format -show_streams {filepath}'
    result = subprocess.run(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    meta = json.loads(result.stdout)

    command = f'ffmpeg -i {filepath} -map 0:v -c copy -f md5 -'
    result = subprocess.run(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    md5 = re.findall(r'MD5=([\da-z]+)', result.stdout)[0]

    return models.Video(
        md5=md5,
        meta=meta,
        extracted=False
    )


def get_signatures_0(src_fp: str) -> Generator[models.Signature, None, None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        dst_path: str = os.path.join(temp_dir, "dst")
        os.mkdir(dst_path)
        subprocess.run(_RUN_CMD_TEMPLATE.format(src_fp, dst_path).split(" "))
        f_names: list[str] = list(
            sorted(
                os.listdir(dst_path),
                key=lambda x: (
                    int(re_list[0])
                    if (re_list := re.findall(r"\d+", x))
                    else x
                )
            )
        )

        for i, file_name in enumerate(f_names, start=1):
            with Image.open(os.path.join(dst_path, file_name)) as im:
                data = np.asarray(im)
                data = [
                    [
                        list(map(int, y))
                        for y in x
                    ]
                    for x in data
                ]
                yield models.Signature(
                    version=0,
                    range=i,
                    meta={
                        "img": {
                            "mode": im.mode,
                            "size": im.size,
                            "data": data,
                        }
                    }
                )
