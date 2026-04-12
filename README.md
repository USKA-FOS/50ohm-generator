# 50ohm.de helvetisierte Version CH

50ohm.de ist die Ausbildungsplattform des DARC e.V., diese wird ab dem Frühjahr 2026 an die schweizerischen Gegebenheiten (Lizenz HB3 / HB9) angepasst und in die zwei weiteren Landessprachen (F/I) übersetzt. Hierfür sind auch Änderungen an diesem Generator notwendig. Bisher wurde implementiert:

- Anpassungen an Logos, Favicons, Schriften und Farbpalette (siehe Issues #2, #3, #15, #16)
- Konsistente Vorwärts/Zurück-Navigation  (siehe Issue #5)
- Diff-Modus für modifizierte Fragen (siehe Issue #12)
- Inhaltsverzeichnisse mit gleicher Nummerierung für alle Editionen (siehe Issue #8).

Dieses Repository enthält den Generator für die Webseite, der mit einem andern [Repository](https://github.com/USKA-FOS/50ohm-contents-ch) als Quelle für die Inhalte arbeitet. Dieses Repository ist ein Fork des Generators, der vom DARC e.V. [hier](https://github.com/DARC-e-V/50ohm) angeboten und entwickelt wird.

## Überblick

Die Ausbildungsmaterialien für die Plattform werden in einem erweiterten Markdownformat geschrieben, intern als DARCdown bezeichnet. Kern des Generators ist ein Parser, der auf [mistletoe](https://github.com/miyuchina/mistletoe) basiert und um zusätzliche Syntax und Ausgabeformate erweitert wurde.

Die möglichen Ausgabeformate sind:
- HTML: [`fifty_ohm_html_renderer.py`](renderer/fifty_ohm_html_renderer.py)
- LaTeX: [`fifty_ohm_latex_renderer`](renderer/fifty_ohm_latex_renderer.py)
- HTML für Slides mit reveal.js: [`fifty_ohm_html_slide_renderer.py`](renderer/fifty_ohm_html_slide_renderer.py)

Prinzipiell lassen sich diese Generatoren auch für andere Quell-Repositories verwenden (so wie es hier für die helvetisierte Version der 50ohm-Plattform der Fall ist). Dies ist insbesondere für andere IARU-Verbände interessant, welche auch 50ohm als Ausbildungsseite implementieren wollen. Der eigentliche Teil des Generators liegt in `src`, insbesondere das Skript ([`build.py`](src/build.py)). In dieser Datei finden sich außerdem weitere Begleitfunktionen zum Renderprozess, z.B. das Übersetzen von Fragennummern in Fragen oder das Kopieren von Assets.

## Mitmachen und Kontakt

Aktuell wird [50ohm.de](https://www.50ohm.de) durch ein kleines ehrenamtliches Entwicklerteam beim DARC e.V. betreut und weiterentwickelt. Die helvetisierte Version wird von einem ebenso kleinen Team im Rahmen eines Projektes der [USKA](https://www.uska.ch) bewirtschaftet. Falls du einen Fehler oder einen Funktionswunsch hast, schreibe gerne ein Issue. Auch über einen PR freuen wir uns!
Wenn du inhaltliche Beiträge hast und diese direkt in der Originalversion des DARC einbringen möchtest, kannst du diese über dieses [Repository](https://github.com/DARC-e-V/50ohm-contents-dl) einreichen.

Bei Anfragen zur Helvetisierung bitte die Email-Adresse [50ohm@uska.ch](mailto:50ohm@uska.ch), bei solche ans DARC-Team [50ohm@darc.de](mailto:50ohm@darc.de) nutzen. Weiterhin findet man viele der Beitragenden im Matrix-Kanal [50ohm Contribution](https://matrix.to/#/#50ohm-contribution:darc.de).

### Python einrichten und Abhängigkeiten installieren

Dieses Projekt wurde mit [`uv`](https://docs.astral.sh/uv/) aufgesetzt, ist aber genauso mit `pip` und `venv` kompatibel.

Wichtig ist, mit der richtigen Python-Version aus der `.python-version` zu arbeiten. Mit `uv` geht das ganz einfach:
```console
$ uv venv
Using CPython 3.12.7
Creating virtual environment at .venv
$ source .venv/bin/activate
```

Die Dependencies müssen aus der `requirements.txt` installiert werden:
```console
$ uv pip sync requirements.txt
```

### Ausführen

Um 50ohm ausführen zu können, muss der Pfad zu einem lokal ausgechecktem Content-Repository in die `config/config.json` eingetragen werden. Ein Beispiel-Content-Repository für deutsche Inhalte findet sich hier: [50ohm-contents-dl](https://github.com/DARC-e-V/50ohm-contents-dl).

Die 50ohm.de-Website wird mit folgendem Befehl vollständig gebaut:

```console
$ python3 ./build.py
```

Anschließend ist der Einstiegspunkt in `build/index.html` zu finden.
