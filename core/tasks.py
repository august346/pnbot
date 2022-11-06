from typing import Optional

from celery import Celery, chord

import algorithms
import models

ALGO_NUMBER = 0

app = Celery(
    'tasks',
    broker_url='amqp://localhost:5672',
    result_backend='redis://localhost:6379/0'
)


@app.task
def download(video_info_dict: dict):
    with algorithms.download(video_info_dict):
        extract.apply(args=[ALGO_NUMBER, video_info_dict])


@app.task
def extract(algo_number: int, video_info_dict: dict):
    video_id, counter = algorithms.get(
        algo_number
    ).extract(video_info_dict)  # type: Optional[int], int

    if video_id:
        compare_all.delay(video_id, video_info_dict)

    return counter


@app.task
def compare_all(video_id: int, video_info_dict: dict):
    another_ids: list[int] = models.Video.ids_to_compare(video_id)

    return chord(
        (
            compare.s(ALGO_NUMBER, video_id, v_id)
            for v_id in another_ids
        ),
        notify_result.s(video_info_dict)
    )()


@app.task
def compare(algo_number: int, id_0: int, id_1: int):
    return algorithms.get(algo_number).compare(id_0, id_1)


@app.task
def notify_result(results: list[tuple[int, int, int]], video_info_dict: dict):
    print(f"{results=}, {video_info_dict=}")
