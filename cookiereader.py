#
# File 'cookiereader.py', part of project 'CookieReader'
# Created on 2121-12-13 by 'jrathert'
#
# https://stackoverflow.com/questions/60416350/chrome-80-how-to-decode-cookies - user Topaco
# https://stackoverflow.com/questions/23153159/decrypting-chromium-cookies/23727331#23727331 - user n8henrie
#

import configparser
import os
import sqlite3
import sys

import secretstorage
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2


def get_cookie_crypto_key():
    # get a key that will be used to decrypt the encrypted cookie values in Chrom{ium|e}s database

    # first read password from linux keychain storage
    bus = secretstorage.dbus_init()
    collection = secretstorage.get_default_collection(bus)
    passwd = ''
    for item in collection.get_all_items():
        if item.get_label() == 'Chrome Safe Storage':
            passwd = item.get_secret()
            break

    # something went wrong that we cannot handle
    if passwd == '':
        return None

    # Now use the password and some default values used by both Chrome and Chromium in OSX and Linux
    # to create and return the key
    salt = b'saltysalt'
    length = 16
    iterations = 1  # 1003 on Mac, 1 on Linux
    return PBKDF2(passwd, salt, length, iterations)


def query_chrome(cookie_file: str, hosts=None):
    # query chromes cookie file for all cookies of the specified hosts (or all)

    if hosts is None:
        hosts = list()

    def clean_padding(x):
        # helper function to get rid of padding and then decode bytestrings
        return x[:-x[-1]].decode('utf8') if len(x) > 0 else ''

    # create the query...
    if len(hosts) > 0:
        where_clause = "where " + " or ".join([f"host_key like '{h}'" for h in hosts])
    else:
        where_clause = ""
    qry = f"select host_key, name, encrypted_value from cookies {where_clause}"

    # ...read (encrypted) cookies from sqlite db...
    con = sqlite3.connect(cookie_file)
    cur = con.cursor()
    results = cur.execute(qry).fetchall()
    cur.close()
    con.close()

    # ...get the necessary decryption key...
    key = get_cookie_crypto_key()
    if key is None:
        print("ERROR: Could not retrieve decryption key - exiting")
        return
    iv = b' ' * 16

    # ...and print the cookies (by decrypting them)
    i = 0
    print("{")
    for host, name, enc_value in results:
        i += 1
        end = ',\n' if i < len(results) else '\n'
        encrypted = enc_value[3:]  # [3:] cuts chrome version prefix
        cipher = AES.new(key, AES.MODE_CBC, IV=iv)
        decrypted = clean_padding(cipher.decrypt(encrypted))
        print(f'    "{name}": "{decrypted}"', end=end)
    print("}")


def query_firefox(cookie_file: str, hosts: list):
    # query chromes cookie file for all cookies of the specified hosts (or all)

    # create the query...
    if len(hosts) > 0:
        where_clause = "where " + " or ".join([f"host like '{h}'" for h in hosts])
    else:
        where_clause = ""
    qry = f"select host, name, value from moz_cookies {where_clause}"

    # ...read cookies from sqlite db...
    con = sqlite3.connect(cookie_file)
    cur = con.cursor()
    results = cur.execute(qry).fetchall()
    cur.close()
    con.close()

    # ...and print them
    i = 0
    print("{")
    for host, name, value in results:
        i = i + 1
        end = ',\n' if i < len(results) else '\n'
        print(f'    "{name}": "{value}"', end=end)
    print("}")


def find_ff_dir(home):
    # try to identify the firefox profile directory
    ff_dir = home + '/.mozilla/firefox/'
    if os.path.isfile(ff_dir + 'profiles.ini'):
        cfg = configparser.ConfigParser()
        cfg.read(ff_dir + 'profiles.ini')
        for s in cfg.sections():
            opts = cfg.options(s)
            if "default" in opts and "path" in opts and cfg.get(s, "default") == '1':
                return cfg.get(s, "path")
    return None


def print_usage():
    # some help
    name = os.path.basename(__file__)
    print(f"Usage: {name} chrome|firefox [-f cookie_file] [ host(s) ]")
    print(f"  chrome|firefox : mandatory, specify what browser cookies you want to read")
    print(f"  -f cookie_file : optional, specify file to read (needed, if program cannot determine file)")
    print(f"  host(s)        : optional, list of hosts/host patterns for which you want to see cookies")
    print(f"Examples:")
    print(f"  # list all cookies from firefox default cookie DB")
    print(f"  $ python {name} firefox ")
    print(f"  # list cookies from specified firefox cookie DB")
    print(f"  $ python {name} firefox -f /home/joe/.mozilla/Profile/cookies.sqlite")
    print(f"  # list all chrome cookies from www.microsoft.com or www.facebook.com")
    print(f"  $ python {name} chrome www.microsoft.com www.facebook.com")
    print(f"  # list cookies stored by *.apple.com domains in specified chrome cookie DB")
    print(f"  $ python {name} chrome -f /tmp/Cookies %.apple.com")


def main():
    # mainly parsing the command line (yes, that can be done better, I know of argparse...)

    # someone might need some help
    if len(sys.argv) < 2 or '-h' in sys.argv:
        print_usage()
        exit(1)

    # one mandatory argument: are we using chrome or firefox
    mode = ''
    if sys.argv[1] not in ["chrome", "firefox"]:
        print_usage()
        exit(1)
    else:
        mode = sys.argv[1]

    # check if some specific file was given and identify where host arguments start
    hosts = list()
    cookie_file = ''
    host_start_idx = 2
    if len(sys.argv) > 2:
        if sys.argv[2] == "-f":
            if len(sys.argv) == 3:
                print_usage()
                exit(1)
            else:
                cookie_file = sys.argv[3]
                host_start_idx = 4
    if len(sys.argv) > host_start_idx:
        hosts = sys.argv[host_start_idx:]

    # if the cookie_file was not specified, we try to guess
    if cookie_file == '':
        home = os.environ['HOME']
        if mode == 'chrome':
            cookie_file = home + '/.config/google-chrome/Default/Cookies'
        else:
            ff_dir = find_ff_dir(home)
            if ff_dir is not None:
                cookie_file = home + '/.mozilla/firefox/' + ff_dir + '/cookies.sqlite'

    # if the cookiefile is still not available or not readable - complain and exit
    if cookie_file == '' or not os.access(cookie_file, os.R_OK):
        print(f"ERROR: Cookie file for {mode} cannot be determined or opened")
        print("Please specify file using the command line switch -f\n")
        print_usage()
        exit(1)

    # all set - do the job
    if mode == 'chrome':
        query_chrome(cookie_file, hosts)
    else:
        query_firefox(cookie_file, hosts)


if __name__ == '__main__':
    main()
