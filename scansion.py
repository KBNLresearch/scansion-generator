#!/usr/bin/python




import xml.etree.ElementTree as ET
import urllib
import urllib2
import re
import time
import codecs
import stresspatterns
import sys
import argparse



"""
This script determines the scansion of the supplied poem. It only supports modern dutch and finds a scansion
as close to a supplied target pattern (default is the iambic pentameter) as possible. Alternative metres are 
supported and can be supplied on the command-line. The input may be plain text or a TEI document.
"""




parser = ET.XMLParser()
parser.parser.UseForeignDTD(True)
parser.entity['nbsp'] = ' '


# return the content of the "l" elements (as a list) from the supplied txt document
def get_lines_from_txt(filename):

	f = codecs.open(filename, "r", "utf-8")
	lines = [l.rstrip() for l in f.readlines()]
	f.close()

        return lines


# return the content of the line elements (as a list) from the supplied XML document
def get_lines_from_xml(filename, line_elmt):
        global parser
        tree = ET.parse(filename, parser)
        root = tree.getroot()

        lines = []
        for l in root.iter(line_elmt):
		line = ""
		for t in l.itertext():
			line = line + t
		lines.append(line.replace('\n', ' ').replace('\r', ''))

        return lines



# convert a stress pattern into a list of candidate scansions and 
# return the one closest (in the levenshtein sense) to the supplied 
# target scansion.
def get_scansion_pattern(stress_pattern, target_scansion):
	wildcard_pattern = get_wildcard_pattern(stress_pattern)

	# expand wildcard patterns
	candidate_patterns = make_copies(wildcard_pattern)

	target_str = "".join(str(d) for d in target_scansion)
	minimum_dist = float("inf")
	best_pattern = []
	for p in candidate_patterns:
		p_str = "".join(str(d) for d in p)
		dist = levenshtein(p_str, target_str)
		if dist == 0:
			return target_scansion
		else:
			if dist < minimum_dist:
				minimum_dist = dist
				best_pattern = p

	return best_pattern
				
			


# for every -1 in the input list we generate two output lists: one with
# a 0 instead of that -1 and a list with a 1 in that same location.
def make_copies(patterns):

	if -1 in patterns:
		p1 = list(patterns)
		p2 = list(patterns)
		p1[p1.index(-1)] = 0
		p2[p2.index(-1)] = 1
		tmp = []
		tmp.extend(make_copies(p1))
		tmp.extend(make_copies(p2))
		return tmp
	else:
		return [patterns]



# return a scansion pattern with '-1' for ambiguous syllables. Basically, 
# only weak-strong and strong-weak transitions get coded as "01" or "10"
# respectively. All other syllables get '-1'.
def get_wildcard_pattern(stress_pattern):
	if len(stress_pattern) == 0:
		return []
	elif len(stress_pattern) == 1:
		return [1]

	if stress_pattern[0] != 3 and stress_pattern[1] != 3:
		if stress_pattern[0] > stress_pattern[1]:
			scansion_pattern = [1]
		elif stress_pattern[0] < stress_pattern[1]:
			scansion_pattern = [0]
		else:
			scansion_pattern = [-1]
	else:
		scansion_pattern = [-1]

	for i in range(1, len(stress_pattern) - 1):
		sprev = stress_pattern[i-1]    
		s = stress_pattern[i]
		snext = stress_pattern[i+1]
		if s == 3 or sprev == 3 or snext == 3:
			scansion_pattern.append(-1)
		elif sprev > s and snext < s:
			scansion_pattern.append(-1)
		elif sprev < s and snext > s:
			scansion_pattern.append(-1)
		elif sprev > s and snext == s:
			scansion_pattern.append(0)
		elif sprev < s and snext < s:
			scansion_pattern.append(1)
		elif sprev > s and snext > s:
			scansion_pattern.append(0)
		elif sprev < s and snext == s:
			scansion_pattern.append(1)
		elif sprev == s and snext > s:
			scansion_pattern.append(0)
		elif sprev == s and snext < s:
			scansion_pattern.append(1)
		else:
			scansion_pattern.append(-1)

	if stress_pattern[-1] == 3 or stress_pattern[-2] == 3:
		scansion_pattern.append(-1)
	elif stress_pattern[-1] > stress_pattern[-2]:
		scansion_pattern.append(1)
	elif stress_pattern[-1] < stress_pattern[-2]:
		scansion_pattern.append(0)
	else:
		scansion_pattern.append(-1)

	return scansion_pattern
	


# compute levenshtein distance between s1 and s2 
def levenshtein(s1, s2):
	l1 = len(s1)
	l2 = len(s2)

	matrix = [range(l1 + 1)] * (l2 + 1)
	for zz in range(l2 + 1):
		matrix[zz] = range(zz,zz + l1 + 1)
	for zz in range(0,l2):
		for sz in range(0,l1):
			if s1[sz] == s2[zz]:
				matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz])
			else:
				matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz] + 1)
	return matrix[l2][l1]




if __name__ == '__main__':

	# iambic pentameter is default
	default_metre = "0101010101"

	# line element (in case the input is XML)
	default_line_elmt = "l"

	# cmd line parsing
	aparser = argparse.ArgumentParser()
	aparser.add_argument('-m', "--metre", required=False, default=default_metre, help='the metre as a string of zeroes and ones', metavar='metre')
	aparser.add_argument('-f', "--file", required=True, help='the input file containing poetry to be scanned', metavar='filename')
	aparser.add_argument('-e', "--element", required=False, default=default_line_elmt, help='the name of the XML element containing a line of verse', metavar='line element')
	aparser.add_argument('-t', "--text", required=False, help='assume the input is plain text', action="store_true")
	aparser.add_argument('-d', "--debug", required=False, help='print debugging info', action="store_true")
	
	args = aparser.parse_args()
	metre = args.metre 
	filename = args.file
	line_elmt = args.element
	debug = args.debug


	# initialize the module
	stresspatterns.init()

	if args.text:
		lines = get_lines_from_txt(filename)
	else:
		lines = get_lines_from_xml(filename, line_elmt)

	metre_num = map(int, metre)

	scansion_pattern_struct = {}
	line_struct = {}
	for l in lines:
		if l.strip() == '': continue
		(words, pauses) = stresspatterns.get_words_from_string(l)
		# first try regular stress patterns
		stress_patterns = stresspatterns.get_stress_patterns(words)
		stress_pattern_string = "".join(stress_patterns) # ignore word boundaries
		stress_pattern_num = map(int, stress_pattern_string)
		scansion_pattern = get_scansion_pattern(stress_pattern_num, metre_num)

		# try "poetic" stress patterns to see if we can get closer to the meter
		stress_patterns_poetic = stresspatterns.get_stress_patterns_poetic(words)
		stress_pattern_string_poetic = "".join(stress_patterns_poetic) # ignore word boundaries
		stress_pattern_num_poetic = map(int, stress_pattern_string_poetic)
		scansion_pattern_poetic = get_scansion_pattern(stress_pattern_num_poetic, metre_num)


		pattern_string = "".join(str(d) for d in scansion_pattern)
		pattern_string_poetic = "".join(str(d) for d in scansion_pattern_poetic)
		if levenshtein(pattern_string, metre) < levenshtein(pattern_string_poetic, metre):
			pattern_string_final = pattern_string
			wildcard_pattern_string = "".join(str(d) for d in get_wildcard_pattern(stress_pattern_num))
		else:
			pattern_string_final = pattern_string_poetic
			wildcard_pattern_string = "".join(str(d) for d in get_wildcard_pattern(stress_pattern_num_poetic))
		
		pattern_string = "".join(str(d) for d in scansion_pattern)
		pattern_string_poetic = "".join(str(d) for d in scansion_pattern_poetic)
		wildcard_pattern_string = wildcard_pattern_string.replace("-1", "?")
		if debug:
			print "LINE: %s --- PATTERN: %s --- CELEX PATTERN: %s --- WILDCARD PATTERN: %s" % (l.encode('utf-8'), pattern_string_final, stress_pattern_string, wildcard_pattern_string)
		else:
			print "%s\t%s" % (l.encode('utf-8'), pattern_string_final)
	
	
	
	
	

