
from MosaifyPy import isDarwin
from MosaifyPy import isLinux
if isDarwin():
    import MosaifyPy_Darwin
if isLinux():
    import MosaifyPy_Linux

from PIL import Image
import os
import json

class Mosaify:
	def __MosaifyPy(self):
	    if isDarwin():
	        return MosaifyPy_Darwin.Mosaify()
	    return None

	def __getMosaicTilePreviewPath(self, _mosaic, _id):
	    if isDarwin():
	        return MosaifyPy_Darwin.getMosaicTilePreviewPath(_mosaic, _id)
	    return ""

	def __getMosaicPreviewPath(self, _mosaic):
	    if isDarwin():
	        return MosaifyPy_Darwin.getMosaicPreviewPath(_mosaic)
	    return ""

	def __getMosaicPath(self, _mosaic):
	    if isDarwin():
	        return MosaifyPy_Darwin.getMosaicPath(_mosaic)
	    return ""

	def __init__(self):
		self.mosaic = self.__MosaifyPy()

	def setTileSize(self, side):
		self.mosaic.setTileSize(side)

	def __pil_image(self, path):
	    im = Image.open(path)
	    im = im.convert('RGBA')

	    cols,rows = im.size
	    s = im.tobytes() # Must keep a reference
	    imgdata = s
	    comp = 4

	    return cols, rows, comp, imgdata

	def addTileImage(self, width, height, comp, imgdata, path, _id):
		self.mosaic.addTileImage(width, height, comp, imgdata, path, _id)

	def addTile(self, _id, path):
		width, height, comp, imgdata = self.__pil_image(path)

		self.mosaic.addTileImage(width, height, comp, imgdata, path, _id)

	def removeTile(self, _id):
		return self.mosaic.removeTileImage(_id)

	def hasTile(self, _id):
		return self.mosaic.hasTileImage(_id)

	def setTileSize(self, side):
		self.mosaic.setTileSize(side)

	def getTileSize(self):
		return self.mosaic.getTileSize()

	def getMosaicTilePreviewPath(self, _id):
		return self.__getMosaicTilePreviewPath(self.mosaic, _id)

	def getTileImage(self, _id):
		path = self.getMosaicTilePreviewPath(_id)
		image = Image.open(path)
		os.remove(path)
		return image

	def generate(self, width, height, comp, imgdata):
		# width, height, comp, imgdata = self.__pil_image(path)
		return self.mosaic.generate(width, height, comp, imgdata)

	def getMosaicMap(self):
		mosaicMap = self.mosaic.getMosaicMap()
		d = json.loads(mosaicMap)
		return json.dumps(d, indent=4)

	def getMosaicPreviewPath(self):
		return self.__getMosaicPreviewPath(self.mosaic)

	def getMosaicImage(self):
		path = self.getMosaicPreviewPath()
		image = Image.open(path)
		os.remove(path)
		return image

	def getMosaicJsonArray(self):
		return self.mosaic.getMosaicJsonArray()

	def getMosaicPath(self):
		return self.__getMosaicPath(self.mosaic)


