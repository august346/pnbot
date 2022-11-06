from typing import Optional, Callable

import scrapy
from scrapy import Request, Selector
from scrapy.http import Response


class StudentkiSpider(scrapy.Spider):
    name = "studentki"
    start_urls = ["https://ru.sex-studentki.guru/videos?"]

    def parse(self, response, i_type: Optional[str] = None, **kwargs):
        match i_type:
            case None:
                yield from (
                    Request(a.link, callback=lambda r: self.parse(r, "page"))
                    for a in response.css(".videos-page").css(".video.trailer").css("a").getall()
                )
                need_yield: bool = False
                for s in response.css(".pagination").css("li"):
                    if need_yield:
                        yield Request(s.css("a"), callback=self.parse)
                        break
                    if "selected" in s.attrib.get("class", "").split(" "):
                        need_yield = True
                return
