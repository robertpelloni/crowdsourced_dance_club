import urllib.parse

def get_streaming_links(title: str, artist: str) -> dict:
    """
    Constructs search deep-links for major streaming platforms.
    In a real production system, this would call Spotify/Apple Music APIs
    to retrieve verified ISRC or track IDs.
    """
    query = f"{artist} {title}"
    encoded_query = urllib.parse.quote(query)

    return {
        "spotify": f"https://open.spotify.com/search/{encoded_query}",
        "apple_music": f"https://music.apple.com/search?term={encoded_query}",
        "youtube": f"https://www.youtube.com/results?search_query={encoded_query}"
    }
