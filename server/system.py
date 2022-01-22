from server.gb_api import GBAPI, SortDirection
from server.requester import RequestPriority


def update_video_index():
    # Loop over all videos available on the Giant Bomb website and add their info to the local database.
    s = GBAPI.select('video').sort('id', SortDirection.ASC).limit(100).priority(RequestPriority.low)
    while not s.is_last_page:
        s.next()
        # TODO Save to database
    return
