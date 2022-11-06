import os
from dataclasses import dataclass
from typing import Callable, Generator, Optional

import comparator
import extractor
import models


@dataclass
class Info:
    _data: dict
    filepath: str
    need_compare: bool
    need_delete_after: bool = False


class Algorithm:
    version: int

    do_extract: Callable[[str], Generator[models.Signature, None, None]]
    do_compare: Callable[[Generator[models.Signature, None, None], Generator[models.Signature, None, None]], models.Compare]

    def __init__(self, version, extract, compare):
        self.version = version
        self.do_extract = extract
        self.do_compare = compare

    def extract(self, info_dict: dict) -> tuple[Optional[int], int]:
        info = Info(info_dict, **info_dict)

        video: models.Video = extractor.collect_video_data(info.filepath)
        if old_video := video.is_duplicate():
            video = old_video
            if cnt := models.Signature.count(video.id, self.version):
                return (
                    video.id if info.need_compare else None,
                    cnt
                )
        else:
            video.save()

        i = 0
        for i, signature in enumerate(self.do_extract(info.filepath), start=1):
            signature.save(video.id)

        video.mark_extracted()

        if info.need_delete_after:
            os.remove(info.filepath)

        return (
            video.id if info.need_compare else None,
            i
        )

    def compare(self, original_id: int, video_id: int):
        if result := models.Compare.get_result(original_id, video_id, self.version):
            return result

        return original_id, video_id, self.do_compare(
            *map(
                models.Signature.set_from_video_id,
                [original_id, video_id]
            )
        ).save(original_id, video_id).result


_algo: dict[int, Algorithm] = {
    a.version: a for a in [
        Algorithm(
            0,
            extractor.get_signatures_0,
            comparator.compare_signatures_0
        )
    ]
}


def get(version: int) -> Algorithm:
    return _algo[version]


def download(src_id: int):
    # TODO
    ...
