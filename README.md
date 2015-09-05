# ttSchweizer
Tischtennis Turnier Software im Schweizer System

## Informationen zum Spielsystem

Das "Schweizer System" ähnelt dem System "jeder gegen jeden", wobei einerseits nicht alle Runden ausgetragen werden und andererseits im Turnierverlauf vor allem Spielerinnen/Spieler ähnlicher Spielstärke gegeneinander spielen.
Durch die feste Rundenanzahl ist der Zeitrahmen eines Turniers sehr gut planbar.
... siehe http://www.bttv.de/sport/commerzbank-sports-more-bavarian-tt-race/infos-spielsystem/

## User Interface von **ttSchweizer**

* Konsolenbasiert
* Robust, stabil
* Eingaben werden mit einfachem Texteditor gemacht
* **ttSchweizer** wird in Verzeichnis mit verschiedenen Textfiles aufgerufen
* **ttSchweizer** kann zu jedem Zeitpunkt ausgeführt werden
* Für jede Runde gibt es ein Textfile: *runde1.tts*, *runde2.tts*, ...
* Ist *rundeN.tts* vollständig erfasst, wird *rundeN+1.tts* erzeugt
* *spieler.tts* enthält Spieler mit ihren TTR Werten
* *runde1.tts* wird durch Losen aus *spieler.tts* erzeugt
* *ergebnis.html* wird nach jedem Aufruf aktualisiert

## Hints

* spieler.tts nach TTR sortieren: `sort -n --field-separator=, --key=2 spieler.tts`
