#!/usr/bin/python
#-coding: UTF-8 -*-

import locale

excludedWords = {
"en": ("the", "this", "that", "and", "or"),
"es": ("el", "la", "los", "las", "de", "del", "un", "o", "y", "a", "al"),
"fr": ("le", "la", "les", "ce", "ces", "de", "du", "des", "un", "ou", "et", "au", "aux")
}

punctuationMarks = {
"en": '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~',
"es": '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~¿¡',
"fr": '~#{[|`\^@]}&"\'(-_)=+^¨$£%*µ,;:!?./§<>²€'
}

diacritics = {
"es": {"á":"a", "é":"e", "í":"i", "ó":"o", "ú":"u", "ü":"u", "ñ":"n"},
"fr": {"é":"e", "è":"e", "à":"a", "ç":"c", "ù":"u", "â":"a", "ê":"e", "î":"i", "ô":"o", "û":"u", "ï":"i", "ü":"u", "ñ":"n"}
}

class Parser():

	def __init__(self, dictionary=None):
		language = locale.getlocale()[0].split("_")[0]
		self.excludedWords = excludedWords[language] if language in excludedWords else ()
		self.punctuationMarks = punctuationMarks[language] if language in punctuationMarks else punctuationMarks["en"]
		self.diacritics = diacritics[language] if language in diacritics else {}
		self.dictionary = set(self._preprocess(dictionary)) if dictionary else set()

	def _preprocess(self, text, maxWordLenght=6):
		text = text.lower()
		text = text.replace("\n", " ")
		for c in self.punctuationMarks:
			text = text.replace(c, "")
		for c in self.diacritics:
			text = text.replace(c, self.diacritics[c])
		words = text.split()
		words = list(filter(lambda w: w not in self.excludedWords, words))
		words = [w[:maxWordLenght] if len(w)>maxWordLenght else w for w in words]
		return words

	def match(self, pattern, string):
		patternWords = self._preprocess(pattern)
		sPatternWords = set(patternWords)
		stringWords = self._preprocess(string)
		sStringWords = set(stringWords)
		if len(sPatternWords-self.dictionary) > 1: return 0
		if len((sPatternWords-(sPatternWords-self.dictionary))-sStringWords) > 0: return 0
		readPointer = 0
		score = 0
		increment = 32
		for word in patternWords:
			try:
				index = stringWords.index(word)
				if index >= readPointer:
					score = score<<(increment-(index-readPointer)) if score > 0 else 1<<(increment-(index-readPointer))
					readPointer = index+1
			except ValueError:
				pass
		return score