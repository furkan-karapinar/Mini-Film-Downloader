import os
import sqlite3
from threading import Thread
from tkinter import ttk, messagebox

from PIL import Image, ImageTk
import tkinter as tk
import io
import webbrowser

from pytube import YouTube


def indirme_fonksiyonu(link):
    downloader = FilmDownloader(link)
    downloader.start()


def veritabanindan_gorselleri_al():
    conn = sqlite3.connect('veritabani.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM filmler")

    for i, row in enumerate(cursor.fetchall()):
        film_id, film_adi, film_resmi, film_linki = row

        # Blob verisini görüntüye dönüştür
        image = Image.open(io.BytesIO(film_resmi))
        image = image.resize((100, 100))  # Görüntü boyutunu değiştirebilirsiniz

        tk_image = ImageTk.PhotoImage(image)

        # Görüntüyü ekranda göster
        label = tk.Label(root, image=tk_image)
        label.grid(row=i // 3 * 4, column=i % 3 * 3, columnspan=3, rowspan=2)

        title_label = tk.Label(root, text=film_adi)
        title_label.grid(row=i // 3 * 4 + 2, column=i % 3 * 3, columnspan=3)

        button = tk.Button(root, text="İndir", command=lambda link=film_linki: indirme_fonksiyonu(link))
        button.grid(row=i // 3 * 4 + 3, column=i % 3 * 3 + 1)

        label.image = tk_image  # Referansı tutmak için

class FilmDownloader:
    def __init__(self, link):
        self.link = link
        self.root = tk.Tk()
        self.root.title("Film İndiriliyor")

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack()

        self.plabel = tk.Label(self.root, text="%0 indirildi")
        self.plabel.pack()

    def download_video(self):
        try:
            yt = YouTube(self.link)
            stream = yt.streams.first()
            total_size = stream.filesize

            def download():
                self.download_path = stream.download()
                messagebox.showinfo("Başarılı", "Film başarıyla indirildi!")
                os.startfile(os.path.dirname(self.download_path))
                self.root.destroy()
            download_thread = Thread(target=download)
            download_thread.start()

            def check_progress():
                while download_thread.is_alive():
                    try:
                        file_size = os.path.getsize(stream.default_filename)
                        downloaded = (file_size / total_size) * 100
                        self.progress['value'] = downloaded
                        self.progress.update_idletasks()
                        self.plabel['text'] = "%" + str(round(downloaded)) + " indirildi"
                    except:
                        continue

            check_progress_thread = Thread(target=check_progress)
            check_progress_thread.start()

        except Exception as e:
            messagebox.showerror("Hata", f"İndirme başarısız: {str(e)}")
            self.root.destroy()

    def start(self):
        self.download_video()
        self.root.mainloop()


root = tk.Tk()
root.title("MoviX - Film İndirme Uygulaması")  # Pencere başlığı
veritabanindan_gorselleri_al()
root.mainloop()
