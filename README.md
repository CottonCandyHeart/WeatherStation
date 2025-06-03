## 🌤️ Domowa Stacja Pogodowa
Aplikacja webowa do monitorowania warunków atmosferycznych w czasie rzeczywistym, z zapisem danych do bazy InfluxDB oraz wizualizacją średnich wartości z ostatnich 7 dni.

## 📦 Technologie
- Python + Flask — backend aplikacji webowej

- JavaScript + HTML/CSS — frontend z dynamicznym odświeżaniem danych

- MQTT — odbieranie danych z czujników

- InfluxDB — baza danych do przechowywania danych historycznych

- Paho MQTT — klient MQTT w Pythonie

## 📊 Funkcje
- Odbieranie danych z tematów MQTT:

- KBDProjektTemp — temperatura

- KBDProjektHum — wilgotność

- KBDProjektLDR — natężenie światła

- Wyświetlanie aktualnych danych w czasie rzeczywistym

- Zapisywanie danych co 30 minut do InfluxDB

- Pobieranie średnich dziennych wartości z ostatnich 7 dni

- Przyjazny, graficzny interfejs użytkownika z ikonami zależnymi od wartości

## 🚀 Uruchomienie projektu
### 1. Wymagania
- Python 3.8+

- InfluxDB (domyślnie działa lokalnie na porcie 8086)

- Połączenie z brokerem MQTT (domyślnie test.mosquitto.org)

### 2. Instalacja zależności
```
pip install flask paho-mqtt influxdb-client
```
### 3. Uruchomienie
- python main.py 

- Aplikacja będzie dostępna pod adresem: http://127.0.0.1:5000
  
> [!WARNING]
> Token InfluxDB został umieszczony w kodzie w celach demonstracyjnych. W projekcie produkcyjnym należy go przenieść do zmiennych środowiskowych.

### 4. Struktura projektu
📁 WeatherStation/ <br/>
├── main.py              # Główna aplikacja Flask <br/>
├── mqtt_client.py       # Obsługa MQTT i zapisy do InfluxDB <br/>
├── templates/ <br/>
│   └── index.html       # Strona główna <br/>
├── static/ <br/>
│   ├── style.css        # Stylizacja <br/>
│   └── img/             # Ikony do wizualizacji danych <br/>
## 🔌 Endpoints
- / — strona główna z odświeżaniem danych <br/>

- /data — aktualne dane pogodowe (JSON)

- /history — średnie dzienne wartości z 7 dni (JSON)

## 📬 Autor
- Weronika Bucewka
- Piotr Kons
