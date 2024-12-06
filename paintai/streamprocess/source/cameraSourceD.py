# service.py
import time

def main():
    with open("service_log.txt", "a") as f:
        while True:
            f.write("Service is running...\n")
            f.flush()
            time.sleep(5)

if __name__ == "__main__":
    main()
