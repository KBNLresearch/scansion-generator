== Waar gaat dit over? ==

Deze software dient om automatisch de scandering van dichtregels te bepalen. Input is een bestand en een patroon van versvoeten (binair gecodeerd). Output (naar standard output) is een overzicht van de regels van het inputgedicht met achter iedere regel zijn scandering.

De software bestaat uit de volgende componenten

* scansion.py: de command-line interface en de meer high-level code;
* stresspatterns.py: module om klemtonen in een dichtregel te bepalen op basis van de klemtooninformatie uit de Celex-data.
* dpw.cd: het Celex-bestand met klemtooninformatie voor een groot aantal modern Nederlandse woorden.



== Algoritmen ==

De scandering wordt intern gecodeerd als een string van nullen en enen. Voor een gegeven dichtregel wordt eerst de relatieve zwaarte van de lettergrepen in de individuele woorden bepaald. Er zijn vier gewichtsklassen voor lettergrepen: zwaar, licht, onbeklemtoond en onbekend. Deze klemtooninformatie wordt bepaald op basis van de Celex-informatie in combinatie met de volgende heuristiek: pas deze twee regels toe, maar alleen als daardoor de uiteindelijk resulterende scandering dichter (in de levenshtein-zin) bij het ideale patroon van versvoeten ligt:

* door middel van een apostrof weggelaten lettergrepen tellen niet mee;
* als een woord eindigt op een klinker, terwijl zijn opvolger begint met een klinker dan worden de twee betreffende lettergrepen als één lettergreep beschouwd met als klemtoonwaarde de hoogste waarde van de twee betrokken lettergrepen.

Met deze klemtooninformatie per woord hebben we nog geen scandering, onder meer omdat veel woorden uit één lettergreep bestaan. Om voor zo veel mogelijk lettergrepen een scandering vast te leggen worden nu de volgende regels toegepast.

* als een lettergreep meer nadruk dan één van zijn buren heeft en tenminste evenveel nadruk als de andere buur, krijgt hij een heffing (gecodeerd als 1);
* als een lettergreep minder nadruk dan één van zijn buren heeft en ten hoogste evenveel nadruk als de andere buur, krijgt hij een daling (gecodeerd als 0).

Na deze bewerking ligt de scandering nog steeds niet altijd vast. Uit de resterende mogelijke scanderingen wordt nu de scandering gekozen die het dichtst (in de levenshtein-zin) bij het doelpatroon ligt.



== Command-line interface ==

python scansion.py -f <filenaam> [-m <patroon>] [-e <regel element>] [-t] [-d]
python scansion.py -h

Het bestand kan zowel platte tekst als een XML-document zijn; default is XML (geef -t op als de invoer platte tekst is). Het programma verwacht dat in de invoer de elementnaam "line" gebruikt wordt om een dichtregel te markeren (zoals in TEI); om een andere elementnaam op te geven kan -e gebruikt worden.

Het patroon is optioneel en moet bestaan uit een string van nullen en enen. De defaultwaarde is "0101010101", de jambische pentameter. 

Met -d wordt een uitgebreider debuggingformaat gebruikt in de uitvoer.

Voorbeeld: 

python scansion.py -f verzen.txt -m 10101010 -t


