<h1>Image Similarity Search Project Dokumentation 09 - Kalenderwoche 5 2022</h1>
<h2>Gruppenmitglieder<br>(Joris Müller, Anne Schlangstedt, Julia Scherschinski, Paul Gronemeyer, Fabian Löffler, Luke Mikat)</h2>

<h2>Fortschritte Frontend</h2>

<h3>Anne (@s82881)</h3>

<b>[#80](https://gitlab.bht-berlin.de/image-similarity-search/image-similarity-search-frontend/-/issues/80) Code kommentieren</b> 

- Code mit Jsdoc dokumentiert
- Jsdoc Dokumentation erzeugt

![](./images/comments_2.png)<br>

![](./images/comments.png)<br>

<b>[#81](https://gitlab.bht-berlin.de/image-similarity-search/image-similarity-search-frontend/-/issues/81) Frontend Meeting</b> 

- aktuelle Branches gemerged
- Fehler in Clusteransicht besprochen

<h3>Fabian (@s78278)</h3>

<b>[#74](https://gitlab.bht-berlin.de/image-similarity-search/image-similarity-search-frontend/-/issues/74) Markierung entfernen falls auf anderes Bild geklickt wird</b> 

- mit einer weiteren if-else-Bedingung in der markImage-Funktion gelöst

<b>[#78](https://gitlab.bht-berlin.de/image-similarity-search/image-similarity-search-frontend/-/issues/78) Legende</b> 

- Legende wurde am rechten oberen Rand des Canvas hinzugefügt
- Legende beinhaltet Informationen zu den Markierungsfarben, Anzahl der eingestellten Cluster und deren Farbe
- Legende aktualisiert sich eigenständig sobald die Anzahl der der Cluster geändert wird
- Style der Legende wurde dem Style der Anwendung angepasst


![](./images/cluster_legende.png)<br>
*Legende*

<b>[#63](https://gitlab.bht-berlin.de/image-similarity-search/image-similarity-search-frontend/-/issues/63) Cluster anzeigen</b>

- Aktualisierungsproblem konnte durch asynchrone Funktion behoben werden.
- wurde in #81 (Frontend Meeting) gemeinsam berarbeit
- noch bestehender Bug:  beim Hochladen von Bildern werden die Images aus den props geschmissen und somit kommt es zu einem Absturz beim aktivieren der Cluster

<b>[#85](https://gitlab.bht-berlin.de/image-similarity-search/image-similarity-search-frontend/-/issues/85) Überarbeitung der StyleSheets</b>

Umsetzung mit SCSS:<br>
- vertikale Scrollbar im body wurde entfernt
- erstellen einer color-scheme-datei (in bearbeitung)
- bisher wurden folgen Dateien angepasst: marksStyle, legendStyle und clusterStyle^

<h3>Luke (@s82765)</h3>

<b>[#75](https://gitlab.bht-berlin.de/image-similarity-search/image-similarity-search-frontend/-/issues/75) Fix Bugs after Merge</b> 

- Aufgrund einer falschen Reihenfolge der URLs aus der MultipleThumbnail Zip, wurden die multipleThumbnail - fetches zunächst entfernt.
- Des Weiteren musste ein uploadedImageCount hinzugefügt werden, um die Ids der hochgeladenen Bilder beim erstellen des nN Objektes anzupassen, da die Ids erhöht wurden, jedoch die anderen uploadedImages aus dem State entfernt wurden. So hatte jedes hochgeladene Bild eine zu hohe Id ab dem zweiten Hochladen von Bildern.

<b>[#79](https://gitlab.bht-berlin.de/image-similarity-search/image-similarity-search-frontend/-/issues/79) fetchmultipleThumbnails in der Infoview</b>

- Das Entpacken und Einbinden wurde bereits implementiert. Es ist allerdings aufgefallen, dass die Thumbnails in einer falschen Reihenfolge ankamen und das zu falschen Darstellung führt.
- Die Thumbnails werden jetzt in korrekter Reihenfolge eingebunden. Die in der Zip mitgeschickten Filenames (die ebenfalls die Ids enthalten) werden nun mit den Ids verglichen, so das diese übereinstimmen.

```javascript
var thumbnailId = regexId.exec(zipEntry)[0];
...
let url = URL.createObjectURL(blob)
var thumbnailData = {url: url, thumbnailId: thumbnailId}
return thumbnailData
```
*Die `thumbnailId` wird aus jeder `zipEntry` gelesen und mit zurückgegeben. Dadurch wird garantiert, dass das Bild mit der Id übereinstimmt.*<br>

<b>[#81](https://gitlab.bht-berlin.de/image-similarity-search/image-similarity-search-frontend/-/issues/81) Frontend Meeting</b> 

- aktuelle Branches gemerged
- Fehler in Clusteransicht besprochen

<b>#73 Dokumentation KW 05</b>

- Dokumentation der letzten Fortschritte aller Gruppenmitglieder für die Präsentation am 02.02.22

<h3>Julia (@s75934)</h3>    

<b>[#76](https://gitlab.bht-berlin.de/image-similarity-search/image-similarity-search-frontend/-/issues/76) Instructions/ Settings </b>

- Neue Komponente mit Modaldialog erstellt
- In der Navigationsleiste anklickbar
- Kleine Bedienungsanleitung

![](./images/instructions.png)<br>
*Instructions*

<h3>Paul (@s82130)</h3>

<b>[#23](https://gitlab.bht-berlin.de/image-similarity-search/image-similarity-search-frontend/-/issues/23) Bilder Stack-Ansicht (D3 Collision Detection) </b>

- Bisher wird über jede Zelle iteriert bei jeder neuen gelieferten Bildkoordinate
- Implementierung ausdenken, bei dem selektiver iteriert wird
- Quadtrees ausprobiert, aber dann hat man keine Kontrolle darüber, wie und wann welche Bilder angezeigt werden
- Bisher noch keine Lösung gefunden
- Aktueller Baustelle: Bilder nach Zellen gruppieren und berechnen, welches angezeigt wird und welches nicht

<br>

<h2>Fortschritte Backend</h2>

### Joris (@s81764)

#### **#65 Access Token für alle Routen**

+ Zuvor wurde das Token nur in der Route `/upload` verwendet
+ Das Token wird nun über die eigene Route `/authenticate` generiert und im header `Api-Session-Token` übergeben
+ Durch Einbindung des Tokens im Frontend durch Luke (@s82765) kann das Token nun in jeder Route übergeben werden  

```HTTP
HTTP/1.0 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 7
Api-Session-Token: Takukm9Xdx2DkS6j0bB7Rw==
Access-Control-Allow-Origin: *
Access-Control-Expose-Headers: Api-Session-Token, Content-Length, Content-Type
```  

__Ausschnitt aus den Response-Header von `/authenticate`__  

#### **#69 Refactor von Resourcen in app.py**

+ Zuvor wurden alle Resourcen in `app.py` angelegt
  + Dadurch wirkt die Datei unleserlich und ist unübersichtlich
+ Die Resourcen wurden in das Package `resources` in `api_package` ausgelagert und werden in app.py nur noch importiert  

![](./images/Issue69_1.png)<br>
__Ausschnitt aus der neuen Dateistruktur__  

#### **#70 Docstrings und typing**

+ Zum besseren Verständnis und um eine mögliche Weiterarbeit mit dem Backend zu ermöglichen, sollen in der finalen Version verschiedene Dokumentationsformen benutzt werden:
  + swagger: Dokumentation aller Routen mit Möglichkeit zum Testen
  + typing: Parameter und Rückgabewerte kennzeichnen
  + docstrings: Beschreibung von der Funktion aller Module, Packages, Klassen und Funktionen
  + pydoc: Aus docstrings generierte Übersicht aller Bestandteile des Backends
+ Die swagger-Dokumentation wurde in #47 realisiert
+ typing und docstrings wurden in diesem Issue bearbeitet
+ die pydoc-Dokumentation wird in #71 bearbeitet  

```py
def search(self, images: np.ndarray, k: int) -> 'Union[Tuple[np.ndarray, np.ndarray], None]':
    """Returns the k nearest neighbours and distances of the flat images in the images array using the current faiss index

    Args:
        images (np.ndarray): array containing the flat images, whose neighbours shall be found
        k (int): value indicating, how many neighbours shall be found. Should be 0 < k < Faiss.get_instance().faiss_index.ntotal

    Returns:
        np.array: Distances to the nearest neighbours
        np.array: Indices of the nearest neighbours
    """
    if not self.has_index: 
        print("No index present!")
        return None
    ...
```

__Ausschnitt aus `faiss.py` als Beispiel für typing und docstring__
