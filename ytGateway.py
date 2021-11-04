from youtube_dl import YoutubeDL

YOUTUBEDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}


def yt_search(query):
    with YoutubeDL(YOUTUBEDL_OPTIONS) as ytdl:
        try:
            # Returns first result of a query
            info = ytdl.extract_info(f"ytsearch:{query}",
                                     download=False)['entries'][0]
            return {"source": info["formats"][0]["url"],
                    "id": info["id"],
                    "title": info["title"]}
        except IndexError as e:
            # This means extract_info returned an empty list
            # TODO?: Better error handling? We can directly check if
            # the list is empty or not
            return
