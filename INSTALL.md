# Aufsetzen des Backends

### (1) Benötigte Software:

- [MongoDB](https://www.mongodb.com/try/download/community)
- [Anaconda](https://www.anaconda.com/)
- Code Editor wie [VSCode](https://code.visualstudio.com/) ist empfohlen, Anaconda Prompt reicht jedoch aus

### (2) Klonen des Backend-Repo

Mit SSH: `git@gitlab.bht-berlin.de:image-similarity-search/image-similarity-search-backend.git`  
Mit HTTPS: `https://gitlab.bht-berlin.de/image-similarity-search/image-similarity-search-backend.git`

### (3) Einrichten der Anacoda Python Umgebung (anaconda environment)

Öffnen eines Kommandozeilenfensters (Anaconda Prompt, VSCode Konsole)  
Mit `cd` in den `server`-Ordner des geklonten Projekts navigieren.  
-> Es ist der richtige Ordner, wenn der Ordner die Datei `environment.yml` enthält (mit `dir` überprüfen)  
Nun wird die Umgebung gebaut:

``` shell
# Erstellen der Umgebung
$ conda env create -f environment.yml

# Aktivieren der Umgebung
$ conda activate iss-backend
```

Die Umgebung kann ebenfalls manuell gebaut werden:

``` shell
# Erstellen der Umgebung
$ conda create --name iss-backend

# Aktivieren der Umgebung
$ conda activate iss-backend

# Installieren der Module
$ conda install -c anaconda python=3.8
$ conda install -c pytorch faiss-cpu
$ conda install -c anaconda flask
$ conda install -c anaconda flask-cors
$ conda install -c conda-forge flask-restful
$ conda install -c anaconda pymongo
$ conda install -c conda-forge python-dotenv
$ conda install -c conda-forge pillow
$ conda install -c conda-forge opentsne>=0.4
$ conda install -c conda-forge m2crypto
$ conda install -c anaconda pandas
$ conda install -c anaconda make
$ conda install -c conda-forge pdoc3
$ pip install flask-swagger-ui
```

Wurde die Umgebung schon erstellt und soll nur nach Änderungen in environment.yml aktualisiert werden, geht dies (im Ordner `server`) mit:

``` shell
$ conda env update -f environment.yml --prune
```  

oder (in Windows):  

``` shell
$ make update_env
```  

### (4) .env Datei

Nun kann der Ordner `server` im Code-Editor geöffnet werden.
In diesem Ordner muss die Datei `.env` erstellt werden (falls nicht schon vorhanden, sonst weiter bei [Schritt 5](#5-einbinden-eines-datasets)). In ihr werden die Umgebungsvariablen gesetzt.  
Alle Variablen, die gesetzt werden müssen, mit Beispielwerten:

``` txt
# Server
BACKEND_HOST=localhost
BACKEND_PORT=8080

# Database
DATABASE_CLIENT=mongodb://localhost:27017/
DATABASE_NAME=ISS_BACKEND_DATABASE

# Dataset directory ("data" is recommended, for .gitignore)
DATA_FOLDER=data

# Maximum width and height of thumbnails
THUMBNAIL_WIDTH=128
THUMBNAIL_HEIGHT=128

# Setting for PCA, which reduces the original dimensions to this value for coordinate calculation with openTSNE 
# Needs to be less than or equal to the number of samples in DATA_FOLDER!
REDUCE_IMAGE_TO_DIMS=50

# Default amount of centroids for k-means clustering
NUM_CENTROIDS=10

# Secret key for flask app, just use a random string (replace example)
FLASK_SECRET_KEY=r@nD0msTR1ng
```

### (5) Einbinden eines Datasets

Falls noch nicht vorhanden, muss der `DATA_FOLDER` (der Name ist in der `.env`-Datei spezifiziert) in dem `server`-Ordner erstellt werden.
In den `DATA_FOLDER` kommen nun alle Bilder des gewünschten Datensatzes. Diese Bilder müssen alle die gleichen Dimensionen haben, sonst wird die Ausführung des Programms unterbrochen.  

### (6) Einstellen des Interpreters und Starten des Servers

Im `server`-Ordner befindet sich die Datei `run.py`, die nun geöffnet werden muss. Nur mit dieser Datei kann der Server gestartet werden.  
Falls dies noch nicht automatisch geschehen ist, muss das vorhin erstellte anaconda environment als Interpreter für die Datei ausgewählt werden.  
In VSCode geht dies über `View > Command Palette > Python: Select Interpreter`. Danach aus den angezeigten Interpretern auswählen:  

``` txt
# Windows
Python 3.8.x 64-bit (conda)
~\anaconda3\envs\iss-backend\python.exe

# Mac
Python 3.8.x 64-bit ('iss-backend': conda)
~/opt/anaconda3/envs/iss-backend/bin/python
```

Falls der gewünschte Interpreter nicht angezeigt wird, kann auch über `+ Enter Interpreter Path` der Pfad manuell ausgewählt werden.

Nun kann die Datei `run.py` ausgeführt werden. Dafür gibt es verschiedene Wege:

- Kommandozeile im Ordner `server`:

    ``` shell
    # Windows
    $ python run.py

    # Mac
    $ python3 run.py
    ```

- In VSCode: `Run > Run Without Debugging` in `run.py`  

- Mit dem Makefile in dem Ordner `server` (in Windows):

    ``` shell
    $ make run
    ```  

### (7) Funktionen testen

Mit der Route `{BACKEND_HOST}:{BACKEND_PORT}/swagger` (für die richtigen Werte bitte [diesen Absatz](#4-env-datei) referenzieren) kann auf die Dokumentation von allen 
verfügbaren Routen zugeriffen werden. Dies ist möglich durch das Modul [Swagger](https://pypi.org/project/flask-swagger-ui/). Auf dieser Dokumentationsroute können ebenfalls
alle Routen getestet werden.  
Außerdem gibt es eine Dokumentation für alle Packages, Module, Klassen und Funktionen durch [pdoc3](https://pdoc3.github.io/pdoc/). Die Startseite ist `./docs/index.html`.  
Neu erstellt werden kann die Dokumentation durch das Ausführen der Datei `doc.py` (für alle Unterordner von `server`).  

### (8) Troubleshooting

Es kann immer wieder dazu kommen, dass sich die benötigten Module ändern und somit die vorher gebaute Umgebung nicht mehr aktuell ist.
Dafür können folgende Schritte helfen:

``` shell
# Falls iss-backend Umgebung aktiviert ist
$ conda deactivate

# Alte Umgebung löschen
$ conda env remove -n iss-backend

# Umgebung erneut erstellen
$ conda env create -f environment.yml

# Umgebung wieder aktivieren
$ conda activate iss-backend
```  

oder:  

``` shell
$ conda env update -f environment.yml --prune
```  

oder (in Windows):  

``` shell
$ make update_env
```  

Außerdem kann es zu Änderungen in der `.env` Datei kommen. In diesem Fall würde das Beispiel in [diesem Absatz](#4-env-datei) aktualisiert werden.