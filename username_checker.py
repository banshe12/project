import aiohttp
import asyncio

class UsernameChecker:
    def __init__(self):
        # A list of 30+ major platforms with their URL templates
        self.platforms = {
            "GitHub": "https://github.com/{}",
            "Instagram": "https://www.instagram.com/{}/",
            "Reddit": "https://www.reddit.com/user/{}",
            "Twitter": "https://twitter.com/{}",
            "Steam": "https://steamcommunity.com/id/{}",
            "YouTube": "https://www.youtube.com/@{}",
            "Pinterest": "https://www.pinterest.com/{}/",
            "Twitch": "https://www.twitch.tv/{}",
            "TikTok": "https://www.tiktok.com/@{}",
            "Snapchat": "https://www.snapchat.com/add/{}",
            "Telegram": "https://t.me/{}",
            "VK": "https://vk.com/{}",
            "Medium": "https://medium.com/@{}",
            "Spotify": "https://open.spotify.com/user/{}",
            "SoundCloud": "https://soundcloud.com/{}",
            "Behance": "https://www.behance.net/{}",
            "Dribbble": "https://dribbble.com/{}",
            "Flickr": "https://www.flickr.com/people/{}",
            "Goodreads": "https://www.goodreads.com/{}",
            "Gumroad": "https://gumroad.com/{}",
            "HackerNews": "https://news.ycombinator.com/user?id={}",
            "Keybase": "https://keybase.io/{}",
            "Last.fm": "https://www.last.fm/user/{}",
            "Letterboxd": "https://letterboxd.com/{}/",
            "MyAnimeList": "https://myanimelist.net/profile/{}",
            "Patreon": "https://www.patreon.com/{}",
            "ProductHunt": "https://www.producthunt.com/@{}",
            "Quora": "https://www.quora.com/profile/{}",
            "Slack": "https://{}.slack.com",
            "SlideShare": "https://www.slideshare.net/{}",
            "Vimeo": "https://vimeo.com/{}",
            "Wattpad": "https://www.wattpad.com/user/{}",
            "WordPress": "https://{}.wordpress.com",
            "About.me": "https://about.me/{}",
        }

    async def check_platform(self, session, platform, username):
        url = self.platforms[platform].format(username)
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return {"platform": platform, "status": "Found", "url": url}
                else:
                    return {"platform": platform, "status": "Not Found", "url": url}
        except Exception as e:
            return {"platform": platform, "status": "Error", "url": url, "error": str(e)}

    async def check_username(self, username):
        async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
            tasks = [self.check_platform(session, platform, username) for platform in self.platforms]
            results = await asyncio.gather(*tasks)
            return [res for res in results if res["status"] == "Found"]

if __name__ == "__main__":
    checker = UsernameChecker()
    found = asyncio.run(checker.check_username("testuser"))
    print(found)
