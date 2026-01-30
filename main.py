import sys
from view import main_window

def main():
    main_window.show()
    sys.exit(main_window.app.exec())

if __name__ == "__main__":
    main()
