# need this file for package importing.

from ColorWell import rgba2tk

def colorRange(n):
	"Generate a set of 'n' distinguishable RGB colors"

	from colorsys import hls_to_rgb
	lValues = [ 0.5, 0.25, 0.75 ]
	layers = min(int(n / 6) + 1, len(lValues))
	remainder = n % layers
	perLayer = (n - remainder) / layers
	colorList = []
	for i in range(layers):
		numColors = perLayer
		if i < remainder:
			numColors += 1
		l = lValues[i]
		s = 1.0
		nc = float(numColors)
		for count in range(numColors):
			h = count / nc
			colorList.append(hls_to_rgb(h, l, s))
	return colorList

