import MosaifyPy
from PIL import Image

class Mosaify:
	def __init__(self):
		self.mosaic = MosaifyPy.Mosaify()

	def setTileSize(self, side):
		self.mosaic.setTileSize(side)

	def __pil_image(self, path):
	    im = Image.open(path)
	    im = im.convert('RGBA')

	    rows,cols = im.size
	    s = im.tobytes() # Must keep a reference
	    imgdata = s
	    comp = 4

	    return cols, rows, comp, imgdata

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


	def generate(self, path):
		width, height, comp, imgdata = self.__pil_image(path)
		return self.mosaic.generate(width, height, comp, imgdata)

	def getMap(self):
		mosaicMap = self.mosaic.getMosaicMap()
		return mosaicMap