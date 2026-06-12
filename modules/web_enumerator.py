import requests
import threading
import queue
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WebEnumerator:
    def __init__(self, base_url, wordlist_path, max_threads=20):
        self.base_url = base_url.rstrip('/')
        self.wordlist_path = wordlist_path
        self.max_threads = max_threads
        self.found_paths = []
        self.lock = threading.Lock()

    def load_wordlist(self):
        try:
            with open(self.wordlist_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logging.error(f"Wordlist not found: {self.wordlist_path}")
            return []

    def check_path(self, path):
        url = f"{self.base_url}/{path}"
        try:
            resp = requests.head(url, timeout=2, allow_redirects=False)
            if resp.status_code in [200, 301, 302, 403]:
                with self.lock:
                    self.found_paths.append({
                        'path': path,
                        'status': resp.status_code,
                        'url': url
                    })
                    logging.info(f"[+] Found: {url} ({resp.status_code})")
        except requests.exceptions.RequestException:
            pass

    def run(self):
        wordlist = self.load_wordlist()
        if not wordlist:
            return

        tasks = queue.Queue()
        threads = []

        def worker():
            while not tasks.empty():
                path = tasks.get()
                self.check_path(path)
                tasks.task_done()

        for _ in range(self.max_threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            threads.append(t)

        for word in wordlist:
            tasks.put(word)

        tasks.join()
        return self.found_paths