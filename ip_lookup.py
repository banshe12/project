import aiohttp
import asyncio

class IPLookup:
    def __init__(self):
        self.api_url = "http://ip-api.com/json/{}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"

    async def lookup(self, ip_or_domain):
        url = self.api_url.format(ip_or_domain)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["status"] == "success":
                            return {"status": "Found", "data": data}
                        else:
                            return {"status": "Not Found", "message": data.get("message", "Unknown error")}
                    else:
                        return {"status": "Error", "message": f"HTTP {response.status}"}
            except Exception as e:
                return {"status": "Error", "message": str(e)}

if __name__ == "__main__":
    ip_lookup = IPLookup()
    result = asyncio.run(ip_lookup.lookup("8.8.8.8"))
    print(result)
