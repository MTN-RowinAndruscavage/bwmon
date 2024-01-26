## Socket server that listens for check-mk-agent connections

import wifi
import os, asyncio
import socketpool
import ipaddress
import time, gc

from sensor_data import *
from net_wifi import *

HOST = ""  # see below
PORT = os.getenv('CHECKMK_PORT', 6556)

# lnx_thermal check format is weird but includes a Perf-o-Meter bar
CMK_TEMPZONE0_THRESH = os.getenv('CMK_TEMPZONE0_THRESH', "|35000|passive|45000|critical")
# Custom check thresholds in format of ";WARNBELOW:WARNABOVE;CRITBELOW:CRITABOVE;MIN;MAX"
CMK_TEMP_THRESH = os.getenv('CMK_TEMP_THRESH', ";15:35;10:45;0;70")
CMK_HUMID_THRESH = os.getenv('CMK_HUMID_THRESH', ";30:60;20:70;0;100")
CMK_MOTION_THRESH = os.getenv('CMK_MOTION_THRESH', ";1;50;;")
CMK_MIC_THRESH = os.getenv('CMK_MIC_THRESH', ";1000;2000;0;")

ACCEPT_TIMEOUT = None
CLIENTS_PER_SERVER = 2

def status_mem(mem_free):
    status_mem = f"""MemTotal:            128 kB
MemFree:             {mem_free:.0f} kB
MemAvailable:        {(128 - mem_free):.0f} kB
Buffers:               0 kB
Cached:                0 kB
SwapCached:            0 kB
Active:                0 kB
Inactive:              0 kB
Active(anon):          0 kB
Inactive(anon):        0 kB
Active(file):          0 kB
Inactive(file):        0 kB
Unevictable:           0 kB
Mlocked:               0 kB
SwapTotal:             0 kB
SwapFree:              0 kB
Dirty:                 0 kB
Writeback:             0 kB
AnonPages:             0 kB
Mapped:                0 kB
Shmem:                 0 kB
KReclaimable:          0 kB
Slab:                  0 kB
SReclaimable:          0 kB
SUnreclaim:            0 kB
KernelStack:           0 kB
PageTables:            0 kB
NFS_Unstable:          0 kB
Bounce:                0 kB
WritebackTmp:          0 kB
CommitLimit:         512 kB
Committed_AS:          0 kB
VmallocTotal:          0 kB
VmallocUsed:           0 kB
VmallocChunk:          0 kB
Percpu:                0 kB
HardwareCorrupted:     0 kB
AnonHugePages:         0 kB
ShmemHugePages:        0 kB
ShmemPmdMapped:        0 kB
FileHugePages:         0 kB
FilePmdMapped:         0 kB
CmaTotal:              0 kB
CmaFree:               0 kB
HugePages_Total:       0
HugePages_Free:        0
HugePages_Rsvd:        0
HugePages_Surp:        0
Hugepagesize:          0 kB
Hugetlb:               0 kB
DirectMap4k:           0 kB
DirectMap2M:           0 kB
DirectMap1G:           0 kB"""
    return status_mem

def status_df(df):
    status_df = f"/dev/uf2 vfat  {df[0]:.0f} {df[1]:.0f} {df[2]:.0f}  {100*(df[1] / df[0]):.0f}% /"
    return status_df

def status():
    status = f"""<<<check_mk>>>
Version: 2.2.0
AgentOS: other
Hostname: {wifi.radio.hostname}
AgentDirectory: /etc/check_mk
DataDirectory: /var/lib/check_mk_agent
SpoolDirectory: /var/lib/check_mk_agent/spool
PluginsDirectory: /usr/lib/check_mk_agent/plugins
LocalDirectory: /usr/lib/check_mk_agent/local
FailedPythonReason:
SSHClient:
<<<uptime>>>
{time.monotonic():.2f} {time.monotonic():.2f}
<<<mem>>>
{status_mem(gc.mem_free() / 1024)}
<<<df_v2>>>
{status_df(sys_df())}
<<<lnx_thermal:sep(124)>>>
thermal_zone0|enabled|acpitz|{sdata['temperature']:.0f}000{CMK_TEMPZONE0_THRESH}
<<<local:sep(0)>>>
P "Env Temperature" temperature={sdata['temperature']:.1f}{CMK_TEMP_THRESH} Temperature {sdata['temperature']:.1f}°C | {sdata['temperature'] * 1.8 + 32:.1f}°F
<<<local:sep(0)>>>
P "Env Humidity" humidity={sdata['humidity']:.1f}{CMK_HUMID_THRESH} Humidity {sdata['humidity']:.1f} %
<<<local:sep(0)>>>
P "Env Motion" motion={sdata['motion_per_minute'].sum()}{CMK_MOTION_THRESH} Motion {sdata['motion']} | {sdata['motion_per_minute'].sum()} per minute
<<<local:sep(0)>>>
P "Env Microphone" microphone={sdata['microphone']:.0f}{CMK_MIC_THRESH} Microphone {sdata['microphone']:.0f}
<<<>>>
"""
    return status

pool = socketpool.SocketPool(wifi.radio)

print("Self IP", wifi.radio.ipv4_address)
HOST = str(wifi.radio.ipv4_address)
server_ipv4 = ipaddress.ip_address(pool.getaddrinfo(HOST, PORT)[0][4][0])
print("Server ping", server_ipv4, wifi.radio.ping(server_ipv4), "ms")

# Newer asyncio streams infrastructure doesn't work on CircuitPython due to dependency on usocket
# Based on https://github.com/anecdata/Socket/blob/main/examples/tcp_server_CircuitPython_NATIVE_async.py

async def tcpserver(port):
    s = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    s.bind(("", port))
    s.listen(CLIENTS_PER_SERVER)
    s.settimeout(ACCEPT_TIMEOUT)
    s.setblocking(False)

    while True:
        try:
            conn, addr = s.accept()
            print(f"Connection to {wifi.radio.ipv4_address}:{PORT} accepted from {addr[0]}:{addr[1]}")
            conn.settimeout(ACCEPT_TIMEOUT)
            conn.setblocking(False)
            conn.sendall(status())
            conn.close()
        except OSError as ex:  # EAGAIN
            pass
        await asyncio.sleep(0)

async def net_socket_main():
    tasks = []
    tasks.append(asyncio.create_task(tcpserver(PORT)))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(net_socket_main())
