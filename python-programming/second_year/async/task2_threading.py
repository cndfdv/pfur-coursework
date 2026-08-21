import threading
import time


def download_file(filename, size):
    download_time = size * 0.1
    print(f"Начало загрузки {filename} ({size} МБ)")

    for i in range(5):
        time.sleep(download_time / 5)
        progress = (i + 1) * 20
        print(f"{filename}: {progress}% загружено")

    print(f"Завершена загрузка {filename}")


def task2_threaded_downloader():
    files = [
        ("document.pdf", 10),
        ("image.jpg", 5),
        ("video.mp4", 20),
        ("archive.zip", 15),
    ]

    start_time = time.time()
    threads = []

    for filename, size in files:
        thread = threading.Thread(target=download_file, args=(filename, size))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    print(f"Общее время загрузки: {end_time - start_time:.2f} секунд")


if __name__ == "__main__":
    task2_threaded_downloader()
