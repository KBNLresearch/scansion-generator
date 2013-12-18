== What is this about? ==

This software is used to automatically determine the stress pattern of a line in verse. The input is a file and a pattern of meter (coded in binary). Output (after standard output) is an overview of the lines of the input poem with its stress pattern after each line. 

The software consists of the following components:

* scansion.py: the command-line interface and the more high-level code;
* stresspatterns.py: module to determine the accent in a line of verse on the basis of the accent information from the Celex-data
* dpw.cd: the Celex file with accent information for a large number of modern Dutch words

== Algorithms ==

The meter is coded internally as a string of ones and zeroes. For any given line of verse firstly the relative weight of the syllables in the individual words is determined. There are four weight classes for syllables: heavy, light, unstressed and unknown. This stress information is determined on the basis of the Celex information in combination with the following heuristics: apply these two rules, but only if the resulting meter lies closer (in the Levenshtein sense) to the ideal pattern of meter: 

* by means of an apostrophe left out syllables do not count;
* if a word ends in a vowel, while its follow-up starts with a consonant, then these two syllables are seen as one syllable with the stress on the highest weighted syllable of the two syllables involved.

With this information of stress per word we do not have the meter yet, among other things because many words consist of one syllable. To determine the meter for as many syllables as possible the following rules are applied:

* if a syllable is stressed more than one of its neighbouring words and at least as much stress as the other neighbouring word then it is upgraded (coded as 1);
* if a syllable is less stressed than one of its neighbouring words and at least as much stressed as the other neighbouring word, then it is downgraded (coded as 0);

After this revision, the meter is still not finalized. From the remaining possible meters the meter is chosen that lies closest (in the Levenshtein sense) to the target pattern. 

A Dutch version of this can be found in README.txt.