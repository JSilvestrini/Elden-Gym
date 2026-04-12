"""
https://github.com/amacati/SoulsGym/blob/master/soulsgym/core/speedhack/speedhack.py

The code is 1:1 besides some renaming of variables that make more sense to me.
This Github will be credited once again within the README.md.

The DLL that is injected was lifted from the same Github mentioned above.
"""

import struct
import time
from pathlib import Path
from multiprocessing import Lock
import pywintypes
import win32api
import win32event
import win32process
import win32file

PROCESS_ALL_ACCESS = 0x000F0000 | 0x00100000 | 0x00000FFF
MEM_CREATE = 0x00001000 | 0x00002000
MEM_RELEASE = 0x00008000
MAX_PATH = 260
PAGE_READWRITE = 0x04

def inject(pid: int, dll_path:  Path):
    """
    Injects the given dll into the process with the given pid.

    Args:
        pid: the process id of the process to inject into
        dll_path: the path to the dll

    Returns:
        None
    """
    p_handle = win32api.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    dll_addr = write_dll_to_process(p_handle, dll_path)
    t_handle = create_thread(p_handle, dll_addr)
    win32event.WaitForSingleObject(t_handle, 5000)
    cleanup(p_handle, t_handle, dll_addr)

def write_dll_to_process(p_handle: int, dll_path: Path) -> int:
    """
    Writes the given dll to the process with the given handle.

    Args:
        p_handle: the handle of the process to inject into
        dll_path: the path to the dll

    Returns:
        the address of the dll in the process

    Raises:
        Exception: if the injection fails
    """
    mem_addr = win32process.VirtualAllocEx(p_handle, 0, MAX_PATH, MEM_CREATE, PAGE_READWRITE)

    if not mem_addr:
        win32api.CloseHandle(p_handle)
        raise Exception("VirtualAllocEx failed")

    if not win32process.WriteProcessMemory(p_handle, mem_addr, str(dll_path).encode("ascii")):
        win32api.CloseHandle(p_handle)
        raise Exception("WriteProcessMemory failed")

    return mem_addr

def create_thread(p_handle: int, dll_addr: int) -> int:
    """
    Creates a remote thread in the process with the given handle.

    Args:
        p_handle: the handle of the process to inject into
        dll_addr: the address of the dll in the process

    Returns:
        the handle of the created thread
    """
    module_addr = win32api.GetModuleHandle("kernel32.dll")
    load_lib_fn = win32api.GetProcAddress(module_addr, "LoadLibraryA")
    t_handle, _ = win32process.CreateRemoteThread(p_handle, None, 0, load_lib_fn, dll_addr, 0)
    return t_handle

def cleanup(p_handle: int, t_handle: int, dll_addr: int):
    """
    Frees allocated memory in the process with the given handle, and closes the handles.

    Args:
        p_handle: the handle of the process to inject into
        t_handle: the handle of the created thread
        dll_addr: the address of the dll in the process

    Returns:
        None
    """
    win32process.VirtualFreeEx(p_handle, dll_addr, 0, MEM_RELEASE)
    win32api.CloseHandle(t_handle)
    win32api.CloseHandle(p_handle)

class SpeedHackConnector():
    """
    Injects the speed hack into the target process and connects the pipe.
    """

    pipe_name = r"\\.\\pipe\\SoulsGymSpeedHackPipe"
    dll_path = Path(__file__).parent / "speedhack.dll"
    _lock = Lock()

    def __init__(self, process_pid: int):
        """
        Connect to the speed hack pipe.

        If the pipe is not yet open, inject the DLL into the game.

        Args:
            process_name: Name of the process to connect to.
        """
        self.pipe = None
        self.target_pid = process_pid
        try:
            self.pipe = self._connect_pipe()
        except pywintypes.error as e:  # Pipe may not be open. In that case, we have to inject first
            if not e.args[0] == 2 and e.args[1] == "CreateFile":
                raise e  # Not the anticipated error on missing pipe, so we re-raise
            inject(self.target_pid, self.dll_path)
            time.sleep(0.1)  # Give the pipe time to come up after the injection (very conservative)
            self.pipe = self._connect_pipe()

    def set_game_speed(self, value: float) -> None:
        """
        Set the game speed to a new value.

        Args:
            value: The new game speed. Can't be lower than 0.

        Returns:
            None
        """
        assert value >= 0
        win32file.WriteFile(self.pipe, struct.pack("f", value))

    def _connect_pipe(self) -> int:
        return win32file.CreateFile(
            self.pipe_name, win32file.GENERIC_WRITE, 0, None, win32file.OPEN_EXISTING, 0, None
        )

    def __del__(self):
        """
        Close the pipe handle on deletion.
        """
        if self.pipe is not None:
            try:
                win32file.CloseHandle(self.pipe)
            except TypeError:
                ...