#! /usr/bin/python

"""
    A simple script helping internet users in mainland China
    accelerating visiting some foreign websit(such as
    stackoverflow etc..)
    Only HTTP on port 80 supported, HTTPS not supported
 
"""

#   Here add whaterver website blocked in China, which will
#   be forwarded to our localhost in this programm.
target_hosts = \
    [
        "ajax.googleapis.com",
        "www.gravatar.com",
        #"cdn.sstatic.net"
    ]
to_ip = "127.0.0.1"

import os
import sys
import platform
if sys.version_info[0] == 3:
    from http.server import HTTPServer as HttpServerClass
    from http.server import SimpleHTTPRequestHandler as HttpServerHandlerClass
elif sys.version_info[0] == 2:
    from BaseHTTPServer import HTTPServer as HttpServerClass
    from SimpleHTTPServer import SimpleHTTPRequestHandler as HttpServerHandlerClass

hosts_linux = "/etc/hosts"
hosts_windows = "C:\\WINDOWS\\system32\\drivers\\etc\\hosts"
#host file backup path
hosts_linux_bak = "/etc/hosts_bak"
hosts_windows_bak = "C:\\WINDOWS\\system32\\drivers\\etc\\hosts_bak"

#   Class to serve a HTTP server
#   Only support GET method and
#   just simplely return a 200 status
class TempHTTPRequestHandler(HttpServerHandlerClass):
    def do_GET(self):
        rsps = b"OK"
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", len(rsps))
        self.end_headers()
        self.wfile.write(rsps)

def check_privilige(os_platform):
    if os_platform == "Windows":
        try:
            with open(hosts_windows, "a"):
                return True
        except PermissionError:
            return False
    elif os_platform == "Linux":
        return os.getuid() == 0

if __name__ == '__main__':
    pf = platform.system()
    if not check_privilige(pf):
        print("Error: Should be run as root or administrator")
        input()
        sys.exit(1)

    hosts_path = ""
    hosts_bak_path = ""
    if pf == "Windows":
        hosts_path = hosts_windows
        hosts_bak_path = hosts_windows_bak
    elif pf == "Linux":
        hosts_path = hosts_linux
        hosts_bak_path = hosts_linux_bak

    #backup hosts file
    with open(hosts_path, "r") as f:
        with open(hosts_bak_path, "w") as f_bak:
            f_bak.write(f.read())
    #set hosts file with target host
    with open(hosts_path, "a") as f:
        f.write("\n")
        for host in target_hosts:
            host_line = "{0}\t{1}\n".format(to_ip, host)
            f.write(host_line)

    #start a simple HTTP server
    #Acctually this is unecessary, howerver we keep it here
    #to add feature in furture
    httpd = HttpServerClass((to_ip, 80), TempHTTPRequestHandler)
    print("Running, MUST PRESS CTRL+C to terminate this script, otherwise content in hosts file my be lost")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        httpd.server_close()
        #reset hosts file
        with open(hosts_bak_path, "r") as f_bak:
            with open(hosts_path, "w") as f:
                f.write(f_bak.read())
        os.remove(hosts_bak_path)
        sys.exit(0)