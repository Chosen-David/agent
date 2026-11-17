"""Conservative local transport liveness checks; never kill an unknown PID."""
import os
import platform
import sys

from .plan_review import sha


def process_scope():
    namespace = os.readlink('/proc/self/ns/pid') if sys.platform.startswith('linux') else None
    return sha({'platform': sys.platform, 'host': platform.node(), 'pid_namespace': namespace})


def pid_running(pid):
    if type(pid) is not int or pid <= 0:
        raise ValueError('valid recorded process PID required')
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        api = ctypes.WinDLL('kernel32', use_last_error=True)
        api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        api.OpenProcess.restype = wintypes.HANDLE
        api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        api.WaitForSingleObject.restype = wintypes.DWORD
        api.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = api.OpenProcess(0x100000, False, pid)  # SYNCHRONIZE, not terminate access
        if not handle:
            if ctypes.get_last_error() in (87, 1168):
                return False
            raise ValueError('cannot verify recorded process absence; keep blocked')
        try:
            result = api.WaitForSingleObject(handle, 0)
            if result not in (0, 258):
                raise ValueError('cannot verify recorded process state')
            return result == 258
        finally:
            api.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True  # Includes unreaped zombies and reused PIDs: conservative.
    except ProcessLookupError:
        return False
    except PermissionError as exc:
        raise ValueError('cannot verify recorded process absence; keep blocked') from exc
