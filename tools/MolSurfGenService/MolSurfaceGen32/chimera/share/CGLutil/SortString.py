
class SortString(str):
	"""strings that sort on criteria other than the text"""

	def __new__(cls, strVal, cmpVal=0):
		obj = str.__new__(cls, strVal)
		obj.strVal = strVal
		obj.cmpVal = cmpVal
		return obj

	def __cmp__(self, other):
		if isinstance(other, SortString):
			return cmp(self.cmpVal, other.cmpVal) \
				or cmp(self.strVal, other.strVal)
		return cmp(self.strVal, other)

	def __lt__(self, other):
		return self.__cmp__(other) < 0
	def __le__(self, other):
		return self.__cmp__(other) <= 0
	def __eq__(self, other):
		return self.__cmp__(other) == 0
	def __ne__(self, other):
		return self.__cmp__(other) != 0
	def __gt__(self, other):
		return self.__cmp__(other) > 0
	def __ge__(self, other):
		return self.__cmp__(other) >= 0

	def lower(self, *args, **kw):
		return SortString(self.strVal.lower(*args, **kw), self.cmpVal)

	def upper(self, *args, **kw):
		return SortString(self.strVal.upper(*args, **kw), self.cmpVal)
