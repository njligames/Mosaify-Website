import platform
import tempfile
import uuid
import time

def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' took {elapsed_time:.4f} seconds to run.")
        return result
    return wrapper

def isDarwin():
	return "Darwin" == platform.uname().system

def isLinux():
	return "Linux" == platform.uname().system

# from MosaifyPy import isDarwin
if isDarwin():
	from MosaifyPy_Darwin import Mosaify
	from MosaifyPy_Darwin import Image
	from MosaifyPy_Darwin import ImageFileLoader
	from MosaifyPy_Darwin import getMosaicPreviewPath as _getMosaicPreviewPath
	from MosaifyPy_Darwin import getMosaicTilePreviewPath as _getMosaicTilePreviewPath
	from MosaifyPy_Darwin import getMosaicPath as _getMosaicPath

if isLinux():
	from MosaifyPy_Linux import Mosaify
	from MosaifyPy_Linux import Image
	from MosaifyPy_Linux import ImageFileLoader
	from MosaifyPy_Linux import getMosaicPreviewPath as _getMosaicPreviewPath
	from MosaifyPy_Linux import getMosaicTilePreviewPath as _getMosaicTilePreviewPath
	from MosaifyPy_Linux import getMosaicPath as _getMosaicPath

# from PIL import Image
from PIL import Image as PILImage
import os
import json


class Image:
	def __pil_image(self, path):
	    im = PILImage.open(path)
	    im = im.convert('RGBA')

	    cols,rows = im.size
	    s = im.tobytes() # Must keep a reference
	    imgdata = s
	    comp = 4

	    return cols, rows, comp, imgdata

	def __init__(self):
		self.image = None

	def open(self, path):
		self.image = ImageFileLoader().load(path)

	def toPILImage(self):
		if None != self.image:
			# Generate a random UUID
			unique_id = uuid.uuid4()

			# Create a random image name with a .png extension
			random_image_name = f"{unique_id}.png"

			tempPath = tempfile.gettempdir() + "/" + random_image_name
			ImageFileLoader().write(tempPath, self.image)
			return PILImage.open(tempPath)
		return None

	def clip(self, x, y, width, height):
		if None != self.image:
			self.image = self.image.clip(x, y, width, height)

class MosaifyPy:
	def __pil_image(self, path):
	    im = PILImage.open(path)
	    im = im.convert('RGBA')

	    cols,rows = im.size
	    s = im.tobytes() # Must keep a reference
	    imgdata = s
	    comp = 4

	    return cols, rows, comp, imgdata, im

	def __init__(self):
		self.mosaic = Mosaify()


	def addTileImage(self, width, height, comp, imgdata, path, _id):
		self.mosaic.addTileImage(width, height, comp, imgdata, path, _id)

	def addTile(self, _id, path):
		width, height, comp, imgdata, im = self.__pil_image(path)

		self.mosaic.addTileImage(width, height, comp, imgdata, path, _id)

	def removeTile(self, _id):
		return self.mosaic.removeTileImage(_id)

	def hasTile(self, _id):
		return self.mosaic.hasTileImage(_id)

	def setTileSize(self, size):
		self.mosaic.setTileSize(size)

	def setPatchSize(self, size):
		self.mosaic.setPatchSize(size)

	def getTileSize(self):
		return self.mosaic.getTileSize()

	def getMosaicTilePreviewPath(self, _id):
		return _getMosaicTilePreviewPath(self.mosaic, _id)

	def getTileImage(self, _id):
		path = self.getMosaicTilePreviewPath(_id)
		image = PILImage.open(path)
		os.remove(path)
		return image

	@time_it
	def generate(self, width, height, comp, imgdata):
		return self.mosaic.generate(width, height, comp, imgdata)

	def getMaxThreads(self):
		return self.mosaic.getMaxThreads()

	def getMosaicMap(self):
		mosaicMap = self.mosaic.getMosaicMap()
		d = json.loads(mosaicMap)
		return json.dumps(d, indent=4)

	def getMosaicPreviewPath(self):
		return _getMosaicPreviewPath(self.mosaic)

	def getMosaicPreviewImage(self):
		path = self.getMosaicPreviewPath()
		image = PILImage.open(path)
		os.remove(path)
		return image

	def getMosaicJsonArray(self):
		return self.mosaic.getMosaicJsonArray()

	def getMosaicPath(self):
		return _getMosaicPath(self.mosaic)
	


