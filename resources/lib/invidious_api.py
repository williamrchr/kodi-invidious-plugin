import requests
import xbmc
from typing import Any, Dict, List, Optional

class InvidiousApiResponseType:
    def __init__(self, data: Dict[str, Any]):
        self.type = data.get("type", "video")
        self.heading = data.get("title", "")
        self.id = data.get("videoId", data.get("authorId", data.get("playlistId", "")))
        self.thumbnail_url = data.get("videoThumbnails", [{}])[0].get("url", "")
        if not self.thumbnail_url:
            self.thumbnail_url = data.get("authorThumbnails", [{}])[0].get("url", "")

class VideoSearchResult(InvidiousApiResponseType):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.description = data.get("description", "")
        self.author = data.get("author", "")
        self.published = data.get("published", 0)
        self.duration = data.get("lengthSeconds", 0)

class ChannelSearchResult(InvidiousApiResponseType):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.description = data.get("description", "")

class PlaylistSearchResult(InvidiousApiResponseType):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.author = data.get("author", "")

class InvidiousAPIClient:
    def __init__(self, instance_url: str, auth: Optional[Dict[str, str]] = None):
        self.instance_url = instance_url.rstrip("/")
        self.base_url = f"{self.instance_url}/api/v1"
        self.session = requests.Session()
        self.username = None
        if auth:
            # Add authentication logic here if required by instance
            self.username = auth.get("username")

    def _make_get_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        # THE FIX: Ensure params is a dictionary before assignment
        if params is None:
            params = {}
        
        # This line was crashing because 'params' was None
        params["local"] = "true" 
        
        url = f"{self.base_url}/{endpoint}"
        xbmc.log(f"invidious API request: {url} with {params}", xbmc.LOGDEBUG)
        
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def fetch_video_information(self, video_id: str) -> Dict[str, Any]:
        return self._make_get_request(f"videos/{video_id}")

    def search(self, query: str) -> List[InvidiousApiResponseType]:
        data = self._make_get_request("search", {"q": query})
        return self._parse_results(data)

    def fetch_channel_list(self, channel_id: str) -> List[InvidiousApiResponseType]:
        data = self._make_get_request(f"channels/{channel_id}/videos")
        return self._parse_results(data)

    def fetch_playlist_list(self, playlist_id: str) -> List[InvidiousApiResponseType]:
        data = self._make_get_request(f"playlists/{playlist_id}")
        return self._parse_results(data.get("videos", []))

    def fetch_special_list(self, list_type: str) -> List[InvidiousApiResponseType]:
        data = self._make_get_request(list_type)
        return self._parse_results(data)

    def _parse_results(self, data: List[Dict[str, Any]]) -> List[InvidiousApiResponseType]:
        results = []
        for item in data:
            item_type = item.get("type", "video")
            if item_type == "video":
                results.append(VideoSearchResult(item))
            elif item_type == "channel":
                results.append(ChannelSearchResult(item))
            elif item_type == "playlist":
                results.append(PlaylistSearchResult(item))
        return results

    def mark_watched(self, video_id: str):
        # Implementation depends on instance API support
        pass
