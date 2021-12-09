# Aufsetzen des Backends

### (1) Benötigte Software:

- [MongoDB](https://www.mongodb.com/) oder [MongoDBCompass](https://www.mongodb.com/products/compass)
- [Anaconda](https://www.anaconda.com/)
- Code Editor wie [VSCode](https://code.visualstudio.com/)

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
$ conda install -c conda-forge opentsne
```

### (4) .env Datei

Nun kann der Ordner `server` im Code-Editor geöffnet werden.
In diesem Ordner muss die Datei `.env` erstellt werden. In ihr werden die Umgebungsvariablen gesetzt.  
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
```

### (5) Einbinden eines Datasets

Falls noch nicht vorhanden, muss der `DATA_FOLDER` (der Name ist in der `.env`-Datei spezifiziert) in dem `server`-Ordner erstellt werden.
In den `DATA_FOLDER` kommen nun alle Bilder des gewünschten Datensatzes. Diese Bilder sollten alle die gleichen Dimensionen haben, sonst wird die Ausführung des Programms unterbrochen.

### (6) Einstellen des Interpreters und Starten des Servers

Im `server`-Ordner befindet sich die Datei `run.py`, die nun geöffnet werden muss. Nur mit dieser Datei sollte der Server gestartet werden.  
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
    python run.py

    # Mac
    python3 run.py
    ```

- In VSCode: `Run > Run Without Debugging` in `run.py`

### (7) Funktionen testen

Mit der Datei `test.http` und der Extension [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) für VSCode
können die Funktionen des Backends getestet werden. Nur der Image Upload sollte in Kombination mit dem Frontend getestet werden.

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

Außerdem kann es zu Änderungen in der `.env` Datei kommen. In diesem Fall würde das Beispiel in [diesem Absatz](#4-env-datei) aktualisiert werden.