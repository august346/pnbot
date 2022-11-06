import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

import tasks


full_pattern = r"^sexstud\d+\.mp4$"
short_pattern = r"^trailer-sexstud\d+\.mp4$"


def extract():
    src = "/Users/ku113p/Downloads/"
    f_names = os.listdir(src)
    f_names = list(filter(lambda x: re.findall(short_pattern, x), f_names))

    args = [
        (
            0,
            {
                "filepath": os.path.join(src, fn),
                "need_compare": True
            }
        ) for fn in f_names
    ]

    for a in args:
        print(tasks.extract(*a))

    # with ThreadPoolExecutor(10) as executor:
    #     results = executor.map(
    #         lambda p: tasks.extract(*p), args
    #     )
    #     for result in results:
    #         print(result)


def info():
    path = "/Users/ku113p/Downloads/sexstud12213.mp4"
    command = f'ffprobe -v quiet -print_format json -show_format -show_streams {path}'
    result = subprocess.run(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    pass


def main():
    extract()


if __name__ == '__main__':
    main()
