# 🎧 Audio-Text Validator (Python GUI)

Prosta, lekka i wydajna aplikacja okienkowa (GUI) napisana w języku Python, służąca do masowej walidacji i korekty transkrypcji plików audio. 

Narzędzie automatyzuje proces przeglądania setek folderów – automatycznie odtwarza plik `.wav`, ładuje powiązany plik `.txt` do edytora i zapisuje zmiany przy przechodzeniu do kolejnego rekordu. Idealne do tworzenia i czyszczenia datasetów do trenowania modeli Machine Learning (np. ASR - Automatic Speech Recognition).

## ✨ Funkcjonalności

* **Automatyczne skanowanie:** Aplikacja przeszukuje wybrany katalog główny i filtruje tylko te podfoldery, które zawierają parę plików `.wav` i `.txt` (ignoruje zbędne pliki).
* **Wbudowany odtwarzacz Audio:** Odtwarzanie dźwięku w tle dzięki bibliotece `pygame` z możliwością pauzowania i odtwarzania od nowa.
* **Interaktywny suwak (Scrubber):** Śledzenie postępu odtwarzania w czasie rzeczywistym i możliwość przewijania nagrania (wykorzystanie biblioteki `wave` do analizy metadanych pliku).
* **Edytor transkrypcji:** Wygodne pole tekstowe do poprawiania błędów w zapisie.
* **Auto-zapis:** Zmiany w pliku `.txt` są automatycznie zapisywane przy przejściu do następnego/poprzedniego folderu.
* **Nawigacja:** Intuicyjne przyciski do przełączania się między rekordami.

## 🛠️ Wymagania i Technologie

Projekt wykorzystuje standardowe biblioteki Pythona oraz jeden zewnętrzny moduł do obsługi audio.

* **Python 3.7+**
* **tkinter:** (wbudowany) do obsługi graficznego interfejsu użytkownika (GUI).
* **pathlib:** (wbudowany) do nowoczesnego i bezpiecznego zarządzania ścieżkami systemowymi.
* **wave:** (wbudowany) do odczytywania długości plików dźwiękowych.
* **pygame:** do bezkolizyjnego odtwarzania plików `.wav` w tle.

## 📦 Instalacja

1. Sklonuj repozytorium na swój dysk:
   ```bash
   git clone https://github.com/WojKie/Transcript_app.git
   cd audio-text-validator
   python -m venv venv
```
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   pip install pygame
   # lub
   python -m pip install pygame-ce
