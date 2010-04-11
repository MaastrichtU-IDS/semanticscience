#!/usr/local/bin/python2.2

FontNameList = [
	"PIL/fonts/clR9x15.pil",
	"PIL/fonts/clR8x16.pil",
	"PIL/fonts/clR8x14.pil",
	"PIL/fonts/clR8x13.pil",
	"PIL/fonts/clR8x12.pil",
	"PIL/fonts/clR8x10.pil",
	"PIL/fonts/clR8x8.pil",
	"PIL/fonts/clR7x14.pil",
	"PIL/fonts/clR7x12.pil",
	"PIL/fonts/clR7x10.pil",
	"PIL/fonts/clR7x8.pil",
	"PIL/fonts/clR6x13.pil",
	"PIL/fonts/clR6x12.pil",
	"PIL/fonts/clR6x10.pil",
	"PIL/fonts/clR6x8.pil",
	"PIL/fonts/clR6x6.pil",
	"PIL/fonts/clR5x10.pil",
	"PIL/fonts/clR5x8.pil",
	"PIL/fonts/clR5x6.pil",
	"PIL/fonts/clR4x6.pil",
]

fontList = []

def TextIcon(master, label, imageSize=(48, 48),
		compress=0, bg=(192, 192, 192), fg=(0, 0, 0)):
	if not fontList:
		_getFonts()
	font, words = _findFont(label, imageSize)
	im = _drawWords(font, words, imageSize, compress, bg, fg)
	from PIL import ImageTk
	return ImageTk.PhotoImage(im)

def _getFonts():
	from PIL import ImageFont
	ttf = 'fonts/freefont/FreeSans.ttf'
	import sys, os
	for p in sys.path:
		path = os.path.join(p, ttf)
		if os.path.exists(path):
			break
	else:
		path = None
	if path:
		try:
			for size in range(16, 7, -1):
				fontList.append(ImageFont.truetype(path, size))
			return
		except ImportError:
			pass
	# no freetype font support
	for fontName in FontNameList:
		fontList.append(ImageFont.load_path(fontName))

def _findFont(label, size):
	# Fonts list is assumed to be sorted by largest to
	# smallest.  So the first font that can accommodate
	# the words is returned.  If no font qualifies, then
	# the largest font that fits the most lines is used
	# (on the assumption that seeing the beginning of
	# many lines provides the most information).  If still
	# no font qualifies, return the smallest font.
	words = label.split()
	while 1:
		best = None
		bestLines = 0
		for font in fontList:
			fits, lines = _checkFont(font, words, size)
			if fits:
				return font, words
			if lines > bestLines:
				best = font
				bestLines = lines
		newWords = _splitWord(words)
		if not newWords:
			break
		words = newWords
	if best:
		return best, words
	return fontList[-1], words

def _checkFont(font, words, imageSize):
	maxWidth, maxHeight = imageSize
	blankSize = font.getsize(" ")
	sizes = [ font.getsize(word) for word in words ]
	lineHeight = max([ size[1] for size in sizes ]) + 2
	lines = 0
	i = 0
	fits = 1
	while i < len(sizes):
		w = sizes[i][0]
		i += 1
		if w > maxWidth:
			# This word does not fit
			fits = 0
		else:
			while i < len(sizes) and w < maxWidth:
				nw = w + blankSize[0] + sizes[i][0]
				if nw > maxWidth:
					break
				i += 1
		lines += 1
	if lines * lineHeight > maxHeight:
		fits = 0
	return fits, lines

def _drawWords(font, words, imageSize, compress, bg, fg):
	maxWidth, maxHeight = imageSize
	blankSize = font.getsize(" ")
	sizes = [ font.getsize(word) for word in words ]
	lineHeight = max([ size[1] for size in sizes ]) + 2
	lines = []
	i = 0
	fits = 1
	while i < len(sizes):
		w = sizes[i][0]
		wordList = [ words[i] ]
		i += 1
		while i < len(sizes) and w < maxWidth:
			nw = w + blankSize[0] + sizes[i][0]
			if nw > maxWidth:
				break
			wordList.append(words[i])
			i += 1
		lines.append(wordList)
	labelHeight = len(lines) * lineHeight - 2
	if compress:
		if maxHeight > labelHeight:
			maxHeight = labelHeight
		imageSize = (maxWidth, labelHeight)
		y = 0
	else:
		y = max(0, (maxHeight - labelHeight) / 2)
	from PIL import Image, ImageDraw
	im = Image.new("RGB", imageSize, bg)
	draw = ImageDraw.Draw(im)
	for wordList in lines:
		words = " ".join(wordList)
		size = font.getsize(words)
		x = max(0, (maxWidth - size[0]) / 2)
		draw.text((x, y + 1), words, font=font, fill=fg)
		if y > maxHeight:
			break
		y += lineHeight
		#draw.line((0, y, maxWidth, y), fill=0xFF0000FF)
	return im

def _splitWord(words):
	import string
	indexLength = [ (len(words[i]), i) for i in range(len(words)) ]
	indexLength.sort()
	indexLength.reverse()
	splitWord = None
	for length, index in indexLength:
		word = words[index]
		splitPlaces = []
		wasLower = word[0] in string.lowercase
		wasPunct = 0
		for i in range(1, length):
			c = word[i]
			if wasLower and c in string.uppercase:
				splitPlaces.append(i)
				wasLower = 0
			else:
				if wasPunct:
					splitPlaces.append(i)
				wasLower = c in string.lowercase
				wasPunct = c in string.punctuation
		if not splitPlaces:
			continue
		bestDelta = length
		best = None
		for place in splitPlaces:
			delta = abs((length - place) - place)
			if delta < bestDelta:
				best = place
				bestDelta = delta
		splitWord = [ index, best ]
		break
	if not splitWord:
		return None
	wl = []
	index, place = splitWord
	for i in range(len(words)):
		if i == index:
			word = words[i]
			wl.append(word[:place])
			wl.append(word[place:])
		else:
			wl.append(words[i])
	return wl

if __name__ == "__main__":
	import sys
	import Tkinter
	label = ' '.join(sys.argv[1:])
	if not label:
		label = "Side View"
	f = Tkinter.Frame()
	f.pack(expand=1, fill="both")
	image = TextIcon(f, label, compress=1)
	b = Tkinter.Button(f, image=image)
	b.pack()
	f.mainloop()
