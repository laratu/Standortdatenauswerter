# Standortdatenauswerter

## Projektüberblick

Der Standortdatenauswerter ermittelt persönliche Informationen, die aus reinen GPS-Standortaufzeichnungen ermittelt werden können. Dieses Projekt bietet die Grundlage für die LocVal [1] WebApp. Diese WebApp bereitet in einer interaktiven App die herausgefundenen Standortinformationen auf.



[1]: https://github.com/laratu/LocVal


## Projekt Starten
Laden Sie Ihre Standortaufzeichnungen als GPX Daten in den Ordner gpxData. Führen Sie dann die main.py aus.
Da keine leeren Ordner hochgeladen werden können müssen sie noch die Ordner 'data', 'csvdata' und 'gpxdata' anlegen.

## Output
In dem Ordner Data finden Sie alle Ausgewerten Informationen als CSV Dateien. 
- alldata: Ihre GPS Aufzeichungen, aber gefiltert
- report: Ein Report ihrer Strecken und Orte
- unique_stops: Alle von ihnen besuchten Orte, klassifiziert und mit Metadaten aus OSM angereichert


## Benutzte Technologien
- Grundlage für die Ermittlung von Stopps & Reisen ist der Stop&Go Klassifier [2].
- Für die Ermittlung von Stoppinformation wurde OpenStreetMap verwendet


[2]: https://github.com/RGreinacher/Stop-Go-Classifier


## Weiterbenutzung der LocVal [1] App
Kopieren Sie den Data Ordner und die Logindatei logindata.csv. Dann müssten sie die WebApp benutzen können. 
