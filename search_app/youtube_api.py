import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re

logger = logging.getLogger(__name__)

def format_duration(duration):
    """Convert ISO 8601 duration to human readable format."""
    # Extract hours, minutes, and seconds using regex
    hours = re.search(r'(\d+)H', duration)
    minutes = re.search(r'(\d+)M', duration)
    seconds = re.search(r'(\d+)S', duration)
    
    # Convert to integers, defaulting to 0 if not found
    h = int(hours.group(1)) if hours else 0
    m = int(minutes.group(1)) if minutes else 0
    s = int(seconds.group(1)) if seconds else 0
    
    # Format as HH:MM:SS or MM:SS
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"

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

        # First, search for videos
        search_response = youtube.search().list(
            q=query,
            part='snippet',
            maxResults=max_results,
            type='video'
        ).execute()

        videos = []
        video_ids = []
        
        # Collect video IDs
        for search_result in search_response.get('items', []):
            try:
                video_id = search_result['id']['videoId']
                video_ids.append(video_id)
            except KeyError as ke:
                logger.warning(f"Missing video ID in response: {ke}")
                continue

        # Get video details including duration
        if video_ids:
            video_response = youtube.videos().list(
                part='contentDetails',
                id=','.join(video_ids)
            ).execute()

            # Create a map of video ID to duration
            duration_map = {}
            for video in video_response.get('items', []):
                try:
                    video_id = video['id']
                    duration = video['contentDetails']['duration']
                    duration_map[video_id] = format_duration(duration)
                except KeyError as ke:
                    logger.warning(f"Missing duration data: {ke}")

            # Combine search results with duration
            for search_result in search_response.get('items', []):
                try:
                    video_id = search_result['id']['videoId']
                    snippet = search_result['snippet']
                    video = {
                        'title': snippet.get('title', 'No Title'),
                        'description': snippet.get('description', 'No Description'),
                        'url': f'https://www.youtube.com/watch?v={video_id}',
                        'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                        'channelTitle': snippet.get('channelTitle', 'Unknown Channel'),
                        'duration': duration_map.get(video_id, 'N/A')
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