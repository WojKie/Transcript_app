import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import pygame
import wave

class AudioValidatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio-Text Validator")
        self.root.geometry("800x600")
        self.root.configure(bg="#2b2b2b")
        
        # --- ZMIENNE STANU (State Management) ---
        self.main_directory = None
        self.valid_folders = [] # Lista ścieżek do folderów, które spełniają warunki
        self.current_index = 0  # Który folder obecnie przeglądamy
        
        self.current_wav_path = None
        self.current_txt_path = None
        
        self.audio_length_seconds = 0.0
        self.is_playing = False

        # Definicja kolorów motywu ciemnego
        self.bg_dark = "#2b2b2b"        # Ciemnoszare tło
        self.bg_medium = "#3c3c3c"      # Średnie tło (dla ramek)
        self.fg_light = "#e0e0e0"       # Jasny tekst
        self.btn_blue = "#1e3a5f"       # Ciemnoniebieski przycisk
        self.btn_green = "#2d5016"      # Ciemnozielony przycisk
        self.btn_yellow = "#5c5c1a"     # Ciemnożółty przycisk
        
        # Inicjalizacja silnika audio
        pygame.mixer.init()
        
        # --- BUDOWA INTERFEJSU (UI) ---
        self.setup_ui()
        
    def setup_ui(self):
        # 1. Górny panel (Przyciski nawigacyjne)
        top_frame = tk.Frame(self.root, pady=10, bg=self.bg_dark)
        top_frame.pack(fill=tk.X)
        
        self.btn_prev = tk.Button(top_frame, text="<< Poprzedni folder", state=tk.DISABLED, command=self.go_prev, bg=self.bg_medium, fg=self.fg_light)
        self.btn_prev.pack(side=tk.LEFT, padx=10)
        
        self.btn_select = tk.Button(top_frame, text="Wybierz Główny Folder", command=self.select_directory, bg=self.btn_blue, fg=self.fg_light)
        self.btn_select.pack(side=tk.LEFT, padx=10, expand=True)

        # Dropdown do wyboru folderu
        self.folder_combo = ttk.Combobox(top_frame, state='readonly', width=30)
        self.folder_combo.set("Wybierz folder główny najpierw")
        self.folder_combo.pack(side=tk.LEFT, padx=10)
        self.folder_combo.bind('<<ComboboxSelected>>', self.on_folder_selected)
        
        self.btn_next = tk.Button(top_frame, text="Zapisz i Następny >>", state=tk.DISABLED, command=self.go_next, bg=self.btn_green, fg=self.fg_light)
        self.btn_next.pack(side=tk.RIGHT, padx=10)
        
        # Etykieta pokazująca postęp (np. "Folder 1 / 10") + przycisk kopiowania
        progress_frame = tk.Frame(self.root, pady=5, bg=self.bg_dark)
        progress_frame.pack(fill=tk.X, padx=20)

        self.lbl_progress = tk.Label(progress_frame, text="Nie wybrano folderu", font=("Arial", 10, "italic"), bg=self.bg_dark, fg=self.fg_light)
        self.lbl_progress.pack(side=tk.LEFT)

        self.btn_copy = tk.Button(progress_frame, text="Kopiuj nazwę", command=self.copy_folder_name, state=tk.DISABLED, bg=self.btn_yellow, fg=self.fg_light)
        self.btn_copy.pack(side=tk.LEFT, padx=10)
        
        # 2. Panel Audio (Suwak i przyciski sterujące)
        audio_frame = tk.Frame(self.root, pady=10, bg=self.bg_dark)
        audio_frame.pack(fill=tk.X, padx=20)

        self.btn_play_pause = tk.Button(audio_frame, text="Play / Od nowa", command=self.play_audio, state=tk.DISABLED, bg=self.bg_medium, fg=self.fg_light)
        self.btn_play_pause.pack(side=tk.LEFT, padx=5)
        
        # Suwak (Scale) używający ttk dla lepszego wyglądu
        self.slider_var = tk.DoubleVar()
        self.slider = ttk.Scale(audio_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.slider_var, command=self.seek_audio, state=tk.DISABLED)
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # 3. Panel Tekstu (Edytor)
        text_frame = tk.Frame(self.root, pady=10, bg=self.bg_dark)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(text_frame, text="Transkrypt (Edytuj, jeśli są błędy):", font=("Arial", 10, "bold"), bg=self.bg_dark, fg=self.fg_light).pack(anchor=tk.W)

        self.text_editor = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 12), bg=self.bg_medium, fg=self.fg_light, insertbackground=self.fg_light)
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        
    # --- LOGIKA APLIKACJI ---

    def sort_folders(self, folders):
        """Sortuje foldery: najpierw te z cyframi leksykograficznie, potem reszta alfabetycznie."""
        def sort_key(item):
            folder_name = item['folder'].name
            has_digits = any(char.isdigit() for char in folder_name)
            return (0 if has_digits else 1, folder_name)

        return sorted(folders, key=sort_key)

    def select_directory(self):
        """Otwiera okno wyboru folderu głównego i skanuje go."""
        selected_dir = filedialog.askdirectory(title="Wybierz folder zawierający podfoldery")
        if not selected_dir:
            return
            
        self.main_directory = Path(selected_dir)
        self.valid_folders = []
        
        
        # Iterujemy przez wszystkie podfoldery w wybranym głównym katalogu
        for subfolder in self.main_directory.iterdir():
            if subfolder.is_dir():
                # Szukamy plików .wav i .txt. Używamy list(generator) aby sprawdzić czy istnieją
                wav_files = list(subfolder.glob("*.wav"))
                txt_files = list(subfolder.glob("*.txt"))
                
                # Jeśli w folderze jest co najmniej jeden wav i jeden txt - dodajemy do listy
                if wav_files and txt_files:
                    self.valid_folders.append({
                        "folder": subfolder,
                        "wav": wav_files[0], # bierzemy pierwszy znaleziony
                        "txt": txt_files[0]  # bierzemy pierwszy znaleziony
                    })
        # Sortuj foldery
        self.valid_folders = self.sort_folders(self.valid_folders)
                    
        if not self.valid_folders:
            messagebox.showwarning("Brak danych", "W wybranym folderze nie ma podfolderów z plikami .wav i .txt")
            return
            
        # Jeśli znaleziono poprawne foldery, ustawiamy się na pierwszym
        self.current_index = 0

        # NAJPIERW wypełnij combobox
        self.folder_combo['values'] = [item['folder'].name for item in self.valid_folders]
        self.folder_combo.current(self.current_index)

        # POTEM załaduj folder
        self.load_current_item()
        
    def load_current_item(self):
        """Ładuje dane z aktualnego folderu do okienka i odtwarza audio."""
        if not self.valid_folders:
            return
            
        # Pobieramy ścieżki
        item = self.valid_folders[self.current_index]
        self.current_wav_path = item["wav"]
        self.current_txt_path = item["txt"]
        
        # Aktualizacja etykiety postępu
        self.lbl_progress.config(text=f"Folder: {item['folder'].name} ({self.current_index + 1} / {len(self.valid_folders)})")
        
        # 1. Ładowanie tekstu
        with open(self.current_txt_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.text_editor.delete("1.0", tk.END) # Czyszczenie pola
        self.text_editor.insert(tk.END, content) # Wstawianie tekstu
        
        # 2. Obliczanie długości audio (potrzebne do suwaka)
        with wave.open(str(self.current_wav_path), 'rb') as w:
            frames = w.getnframes()
            rate = w.getframerate()
            self.audio_length_seconds = frames / float(rate)
            
        # Konfiguracja suwaka
        self.slider.config(to=self.audio_length_seconds, state=tk.NORMAL)
        self.btn_play_pause.config(state=tk.NORMAL)
        
        # Zarządzanie stanem przycisków
        # self.btn_prev.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        # self.btn_next.config(state=tk.NORMAL if self.current_index < len(self.valid_folders) - 1 else tk.DISABLED)
        # Przyciski zawsze aktywne (zapętlenie)
        self.btn_prev.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.NORMAL)
        self.btn_copy.config(state=tk.NORMAL)

        # Synchronizuj combobox
        # if len(self.valid_folders) > 0:
        #     self.folder_combo.current(self.current_index)
        
        # 3. Odpalanie audio
        self.play_audio()

    def play_audio(self):
        """Uruchamia odtwarzanie pliku WAV."""
        if self.current_wav_path:
            pygame.mixer.music.load(str(self.current_wav_path))
            pygame.mixer.music.play()
            self.is_playing = True
            self.update_slider_loop() # Uruchamiamy pętlę odświeżającą suwak
        
    def seek_audio(self, value):
        """Wykonywane, gdy użytkownik przesunie suwak."""
        if not self.is_playing:
            return
        # value to string z aktualną pozycją suwaka (w sekundach), trzeba zrzutować na float
        pos_seconds = float(value)
        # pygame.mixer.music.set_pos działa dla WAV podając czas w sekundach
        pygame.mixer.music.play(start=pos_seconds)
        
    def update_slider_loop(self):
        """Cyklicznie aktualizuje pozycję suwaka na podstawie trwania audio."""
        if pygame.mixer.music.get_busy(): # Jeśli gra muzyka
            # get_pos() zwraca milisekundy od momentu wywołania .play()
            current_time_ms = pygame.mixer.music.get_pos() 
            if current_time_ms > 0:
                # To jest prosty "hack" na synchronizację, jeśli przewijamy - wymaga odrębnego śledzenia
                # Dla uproszczenia w pierwszej wersji, suwak tylko śledzi domyślny playback
                current_time_sec = current_time_ms / 1000.0
                self.slider_var.set(current_time_sec)
                
            # Powtórz tę funkcję za 100ms
            self.root.after(100, self.update_slider_loop)
            
    def save_transcript(self):
        """Zapisuje zawartość pola tekstowego do pliku .txt."""
        if self.current_txt_path:
            content = self.text_editor.get("1.0", tk.END).strip()
            with open(self.current_txt_path, "w", encoding="utf-8") as f:
                f.write(content)
    def copy_folder_name(self):
        """Kopiuje nazwę aktualnego folderu do schowka."""
        if not self.valid_folders:
            return

        folder_name = self.valid_folders[self.current_index]['folder'].name
        self.root.clipboard_clear()
        self.root.clipboard_append(folder_name)
        self.root.update()  # Wymaga Tkinter aby zaktualizować schowek

        # Zmień tekst przycisku na potwierdzenie
        self.btn_copy.config(text="✓ Skopiowano")

        # Przywróć tekst po 2 sekundach
        self.root.after(2000, self.reset_copy_button)

    def reset_copy_button(self):
        """Przywraca oryginalny tekst przycisku kopiowania."""
        self.btn_copy.config(text="Kopiuj nazwę")
    
    def on_folder_selected(self, event):
        """Obsługuje wybór folderu z comboboxa."""
        if not self.valid_folders:
            return

        self.save_transcript()
        self.current_index = self.folder_combo.current()
        pygame.mixer.music.stop()
        self.load_current_item()

    # def go_next(self):
    #     """Zapisuje zmiany i przechodzi do następnego folderu."""
    #     self.save_transcript()
    #     if self.current_index < len(self.valid_folders) - 1:
    #         pygame.mixer.music.stop()
    #         self.current_index += 1
    #         self.load_current_item()
    def go_next(self):
        """Zapisuje zmiany i przechodzi do następnego folderu (zapętlenie)."""
        self.save_transcript()
        pygame.mixer.music.stop()
        self.current_index = (self.current_index + 1) % len(self.valid_folders)
        self.load_current_item()
        self.folder_combo.current(self.current_index)

    # def go_prev(self):
    #     """Przechodzi do poprzedniego folderu (też zapisuje profilaktycznie zmiany)."""
    #     self.save_transcript()
    #     if self.current_index > 0:
    #         pygame.mixer.music.stop()
    #         self.current_index -= 1
    #         self.load_current_item()
    def go_prev(self):
        """Przechodzi do poprzedniego folderu (zapętlenie)."""
        self.save_transcript()
        pygame.mixer.music.stop()
        self.current_index = (self.current_index - 1) % len(self.valid_folders)
        self.load_current_item()
        self.folder_combo.current(self.current_index)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioValidatorApp(root)
    root.mainloop()