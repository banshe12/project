from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

class EXIFExtractor:
    @staticmethod
    def get_labeled_exif(exif):
        labeled = {}
        for tag, value in exif.items():
            decoded = TAGS.get(tag, tag)
            labeled[decoded] = value
        return labeled

    @staticmethod
    def get_geotagging(exif):
        if not exif:
            return None

        geotagging = {}
        for tag, value in exif.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    geotagging[sub_decoded] = value[t]

        return geotagging

    @staticmethod
    def get_decimal_from_dms(dms, ref):
        degrees = dms[0]
        minutes = dms[1]
        seconds = dms[2]

        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ["S", "W"]:
            decimal = -decimal
        return decimal

    @staticmethod
    def get_coordinates(geotags):
        lat = EXIFExtractor.get_decimal_from_dms(geotags["GPSLatitude"], geotags["GPSLatitudeRef"])
        lon = EXIFExtractor.get_decimal_from_dms(geotags["GPSLongitude"], geotags["GPSLongitudeRef"])
        return lat, lon

    def extract(self, image_path):
        try:
            image = Image.open(image_path)
            exif = image._getexif()
            if not exif:
                return {"status": "Not Found", "message": "No EXIF data found"}

            labeled = self.get_labeled_exif(exif)
            geotags = self.get_geotagging(exif)
            coords = None
            if geotags and "GPSLatitude" in geotags and "GPSLongitude" in geotags:
                try:
                    coords = self.get_coordinates(geotags)
                except Exception as e:
                    print(f"Error parsing coordinates: {e}")

            metadata = {k: str(v) for k, v in labeled.items() if k != "GPSInfo"}
            return {"status": "Found", "metadata": metadata, "coords": coords}
        except Exception as e:
            return {"status": "Error", "message": str(e)}

if __name__ == "__main__":
    extractor = EXIFExtractor()
    # In a real environment, you'd provide a path to an actual image.
    # result = extractor.extract("test.jpg")
    # print(result)
    print("EXIFExtractor loaded")
