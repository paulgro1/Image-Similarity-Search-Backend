# Image Similarity Search Backend

Heutzutage gewinnt die Ähnlichkeitssuche auch in unserem Alltag mehr Bedeutung und ist somit fast nicht mehr wegzudenken.
Sie taucht in vielen verschiedenen Themenbereichen auf. Allein wenn wir im Internet etwas herumsurfen stoßen wir auf Werbung, die beispielsweise auf Grund von bestimmten Suchanfragen oder Käufen, für uns zusammengestellt wurde. Sie zeigt uns Dinge, die ähnlich aussehen wie, die die wir schon besitzen oder die uns potentiell gefallen könnten.
Auch dieses Projekt beschäftigt sich mit der Thematik der Ähnlichkeitssuche.
In dem Rahmen eines Semesters haben sich sechs Studenten zusammengefunden um gemeinsam an einer Singlepage-Applikation zu arbeiten.
Mit Hilfe von Back- und Frontend ließ sich eine Schnittstelle entwickeln, die es möglich gemacht hat mathematische Berechnungen benutzerfreundlich visuell darzustellen.
Man kann beliebige Bild-Datensätze in einem angepassten Koordinatensystem erkunden und sich einen genaueren Überblick über die bestimmten Daten geben lassen.
Es gibt die Möglichkeit sich die ähnlichsten Bilder eines bestimmten Bildes, ob hochgeladen oder ausgewählt, ausgeben zu lassen. Hier bekommt man detaillierte Informationen wie den Namen des Bildes, deren prozentuale Ähnlichkeit und die genaue Distanz.

Im funktionalen Teil der Applikation wurden grundlegende Berechnungen durchgeführt, um diese dann zuletzt optisch darzustellen. 
Das große Feature der Ähnlichkeitssuche wurde mittels einer Such-Open-Source-Bibliothek namens FAISS, umgesetzt. Hier wurden die RGB- Werte der jeweiligen Bilder ermittelt, diese in Vektoren umgewandelt und deren Dimension minimiert, um diese in einem Index zu speichern.
Das heißt konkret, wenn man ein Bild in der Applikation auswählt oder hochlädt wird dieses mit jedem Bild im Datensatz verglichen. Dieser Vergleich unterliegt der euklidischen Distanz, die den Abstand zweier Vektoren berechnet. 
Des Weiteren finden die Berechnungen, der jeweiligen Koordinaten der angezeigten Bilder statt, die auf den Faiss Ergebnissen beruhen. 


Zum Aufsetzen und Starten des Backend Servers bitte die Schritte in [INSTALL.md](INSTALL.md) befolgen.

### Gruppenstruktur

- Frontend: Paul, Anne, Fabian
- Backend: Joris, Julia, Luke

### Tools

- React Frontend (eventuell D3.js Bibliothek)
- Python Server Backend (Django oder Flask) 
- Nutzung der FAISS Library und NumPy

### Anforderungen

- Single Page Anwendung 
- Dataset (Gesichter/Tiere)


### Dataset

- Lizenz und Quellen :
https://www.kaggle.com/ashwingupta3012/human-faces/metadata - CC0: Public Domain, No Copyright

### Dokumentation

- https://gitlab.beuth-hochschule.de/image-similarity-search/image-similarity-search-backend/-/tree/development/documentation

### Prototyp

- https://xd.adobe.com/view/41982007-401c-4e0d-803e-edce7190e816-14cb/
