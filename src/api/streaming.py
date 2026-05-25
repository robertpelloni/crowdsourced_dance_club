import urllib.parse

def get_streaming_links(title: str, artist: str) -> dict:
    """
    Constructs search deep-links for major streaming platforms.
    """
    query = f"{artist} {title}"
    encoded_query = urllib.parse.quote(query)

    return {
        "spotify": f"https://open.spotify.com/search/{encoded_query}",
        "apple_music": f"https://music.apple.com/search?term={encoded_query}",
        "youtube": f"https://www.youtube.com/results?search_query={encoded_query}"
    }
