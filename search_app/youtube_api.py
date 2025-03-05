import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

def search_youtube(api_key, query, max_results=5):
    """
    Searches YouTube for videos based on a query.

    Args:
        api_key: Your YouTube Data API v3 key.
        query: The search query string.
        max_results: The maximum number of results to return.

    Returns:
        A list of dictionaries, where each dictionary represents a video.
        Returns None if an error occurs.
    """
    logger.info(f"search_youtube called with query: {query}")
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)

        search_response = youtube.search().list(
            q=query,
            part='snippet',
            maxResults=max_results,
            type='video'
        ).execute()

        videos = []
        for search_result in search_response.get('items', []):
            try:
                video_id = search_result['id']['videoId']
                snippet = search_result['snippet']
                video = {
                    'title': snippet.get('title', 'No Title'),
                    'description': snippet.get('description', 'No Description'),
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                    'channelTitle': snippet.get('channelTitle', 'Unknown Channel')
                }
                videos.append(video)
            except KeyError as ke:
                logger.warning(f"Missing data in response: {ke}")

        return videos

    except HttpError as e:
        logger.error(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None