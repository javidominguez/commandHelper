#-coding: UTF-8 -*-

import locale

excludedWords = {
"en": ("the", "this", "that", "and", "or"),
"es": ("el", "la", "los", "las", "de", "del", "un", "o", "y", "a", "al")
}

punctuationMarks = {
"en": '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~',
"es": '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~¿¡'
}

class Parser():

	def __init__(self, dictionary=None):
		language = locale.getlocale()[0].split("_")[0]
		self.excludedWords = excludedWords[language]
		self.punctuationMarks = punctuationMarks[language]
		self.dictionary = set(self._preprocess(dictionary)) if dictionary else set()

	def _preprocess(self, text):
		text.replace("\n", " ")
		for c in self.punctuationMarks:
			text = text.lower().replace(c, "")
		words = text.split()
		return list(filter(lambda w: w not in self.excludedWords, words))

	def match(self, pattern, string):
		patternWords = self._preprocess(pattern)
		stringWords = self._preprocess(string)
		readPointer = -1
		score = 1
		for word in patternWords:
			try:
				index = stringWords.index(word)
				#@ if readPointer<0: readPointer=index
				if index >= readPointer:
					score = score<<(32-(index-readPointer)) if score > 0 else 1<<(32-(index-readPointer))
					readPointer = index+1
				else:
					score = score>>8
			except ValueError:
				if len(word)>6:
					try:
						index = [w[:6] if len(w)>6 else w for w in stringWords].index(word[:6])
						if index >= readPointer:
							score = score<<(24-(index-readPointer)) if score > 0 else 1<<(24-(index-readPointer))
							readPointer = index+1
					except ValueError:
						if word in self.dictionary:
							return 0
						else:
							score = score>>48
				else:
					if word in self.dictionary:
						return 0
					else:
						score = score>>48
		return score