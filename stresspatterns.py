#!/usr/bin/python
# coding=utf-8



import re
import codecs
import unicodedata



celex_stress_pattern_map = {} 

diphtongs = ["aa", "uu", "oo", "ie", "ei", "ij", "ui", "ou", "ee"]
vowels = ["a", "e", "i", "o", "u", "y"]



# get the words (in the original order) from the file as a list;
# also return a list of positions of pauses (commas, sentence endings)
def get_words_from_file(filename):
	f = codecs.open(filename, encoding='utf-8')
	txt = f.read()
	f.close()
	return get_words_from_string(txt)


# get the words (in the original order) from the string as a list;
# also return a list of positions of pauses (commas, sentence endings)
def get_words_from_string(txt):
	chunks = txt.split()
	words = []
	pauses = []
	for i in range(0, len(chunks)):
		w = chunks[i]
		if w.endswith(",") or w.endswith(":") or w.endswith(";"):
			pauses.append((i, w[-1]))
		elif w.endswith("!") or w.endswith("?"):
			pauses.append((i, w[-1]))
		elif w.endswith("."):
			if i < len(chunks) - 1:
				if  re.search("[A-Z]", chunks[i+1]):
					pauses.append((i, w[-1]))
			else:
				pauses.append((i, w[-1]))
		words.append(re.sub('[:.,!?;]', '', w).lower())

	return (words, pauses)
		

# get the number of syllables
def get_num_syllables(word):
	
	global diphtongs
	global vowels

	count = 0
	i = 0
	while i < len(word):
		
		if i < len(word) - 1:
			if word[i] + word[i+1] in diphtongs:
				count = count + 1
				i = i + 1
			elif word[i] in vowels:
				count = count + 1
		elif word[i] in vowels:
			count = count + 1

		i = i + 1
		

	return count


# return the stress patterns for each word in the supplied list (respecting
# the original order)
def get_stress_patterns(words):

	global celex_dpw_filename

	stress_patterns = []

	for w in words:
		# remove diacritics
		w = remove_accents(w)
		# remove non-word chars prior to matching against celex
		regex = re.compile("[^A-Za-z]", re.UNICODE)
		w = re.sub(regex, '', w)
		if w in celex_stress_pattern_map:
			stress_patterns.append(celex_stress_pattern_map[w])
		else:
			# count the number of syllables
			num_syllables = get_num_syllables(w)
			if num_syllables > 1:
				stress_patterns.append("3" * num_syllables) 
			else:
				stress_patterns.append("2") 

	return stress_patterns



# return the stress patterns for each word in the supplied list (respecting
# the original order), but:
#	- ignore elided one-syllable words ("'t");
#	- treat neighbouring vowels on both sides of a word boundary as one syllable.
def get_stress_patterns_poetic(words):

	global celex_dpw_filename

	stress_patterns = []

	for i in range(0, len(words)):
		w = words[i]
		# remove diacritics
		w = remove_accents(w)
		# remove non-word chars prior to matching against celex
		regex = re.compile("[^A-Za-z]", re.UNICODE)
		w = re.sub(regex, '', w)
		# count the number of syllables
		num_syllables = get_num_syllables(w)
		if num_syllables == 0: 
			continue
		if w in celex_stress_pattern_map:
			stress_patterns.append(celex_stress_pattern_map[w])
		else:
			if num_syllables > 1:
				stress_patterns.append("3" * num_syllables) 
			else:
				stress_patterns.append("2")

		# contract syllables if needed and take the value of the strongest syllable as the stress
		# value for the new syllable (since we use "3" for unknown stress, this also propagates
		# the uncertainty of one of the contracted syllables to the the new syllable).
		if len(stress_patterns) > 1:
			if endswith_diphtong_or_vowel(words[i-1]) and startswith_diphtong_or_vowel(words[i]):
				if stress_patterns[-1] > stress_patterns[-2]:
					del stress_patterns[-2]
				else:
					del stress_patterns[-1]

	return stress_patterns



# return True iff the word ends with a diphtong or vowel
def endswith_diphtong_or_vowel(word):
	global diphtongs
	global vowels

	for d in diphtongs + vowels:
		if word.endswith(d):
			return True
	return False


# return True iff the word starts with a diphtong or vowel
def startswith_diphtong_or_vowel(word):
	global diphtongs
	global vowels
	for d in diphtongs + vowels:
		if word.startswith(d):
			return True
	return False	


# normalize string to ascii
def remove_accents(string):
	nkfd_form = unicodedata.normalize('NFKD', unicode(string))
	return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])



# initialize the celex stress pattern datastructure
def init():
	celex_dpw_filename = "dpw.cd" 

	f = codecs.open(celex_dpw_filename, encoding='utf-8')
	lines = f.readlines()
	f.close()

	for l in lines:
		fields = l.split("\\")	
		word = fields[1]
		pattern = fields[4]
		syllables = pattern.split("-")
		stress_pattern = ""
		for s in syllables:
			# stressed
			if s.startswith("'"):
				stress_pattern = stress_pattern + "2"
			# sjwa
			elif "@" in s:
				stress_pattern = stress_pattern + "0"
			# unstressed
			else:
				stress_pattern = stress_pattern + "1"
		celex_stress_pattern_map[word.lower()] = stress_pattern







if __name__ == '__main__':

	init()

        filename = "awater.txt"

        (words, pauses) = get_words_from_file(filename)
	stress_patterns = get_stress_patterns(words)

	pauses_pointer = 0
	for i in range(0, len(words)):
		print "word: %s, stress pattern: %s" % (words[i].encode('utf-8'), stress_patterns[i].encode('utf-8'))
		if pauses_pointer < len(pauses) and i == pauses[pauses_pointer][0]:
			print "PAUSE %s" % pauses[pauses_pointer][1]
			pauses_pointer = pauses_pointer + 1





