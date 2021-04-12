import multiprocessing as mp
from hyo2.qax.app import gui

if __name__ == "__main__":
    mp.freeze_support()
    gui.gui()
