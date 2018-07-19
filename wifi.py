'''
MIT License

Copyright (c) 2018 Fabricio Roberto Reinert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import sys
import subprocess
import argparse
import locale
import os
import json


class Storage:
    """WLAN Profile Storage"""

    storage = dict()

    def add_to_storage(self, key, val):
        """Update a single key and value"""
        self.storage[key] = val
        return self.storage[key]

    def bulk_storage_update(self, profiles):
        """Update the storage by a dictionary"""
        self.storage.update(profiles)
        return self.storage

    def get_by_key(self, key):
        """Keyfind"""
        return self.storage[key]

    def export(self, output):
        if output in ["txt", "json"]:
            filename = "wlan_profiles." + output

        # Json Export
        if output == "json":
            try:
                with open(filename, "w") as fopen:
                    json.dump(self.storage, fopen)
                return filename
            except:
                return "Operation Error"

        # Text File Export
        if output == "txt":
            try:
                with open(filename, "w") as fopen:
                    for k, v in self.storage.items():  # iterating freqa dictionary
                        fopen.write(k + "\t" + v)
                return filename
            except:
                return "Operation Error"

    def __repr__(self):
        return self.storage.__str__()


class Profiler:
    """Windows WLAN Profiler"""

    def __init__(self, lang):
        self.lang = lang
        self.lang_vars = {
            "pt_BR": {
                "profiles": "Todos os Perfis de Usu\\xa0rios",
                "profile": "Conte\\xa3do da Chave",
            }
        }

    def get_profiles(self):
        """Get all profiles"""
        data = (
            subprocess.check_output(["netsh", "wlan", "show", "profiles"])
            .decode("utf-8", errors="backslashreplace")
            .split("\r\n")
        )
        profiles = [
            i.split(":")[1][1:]
            for i in data
            if self.lang_vars[self.lang]["profiles"] in i
        ]
        return profiles

    def get_passwords_from_profiles(self):
        """Get all passwords from profiles"""
        memchache = dict()
        for i in self.get_profiles():
            try:
                results = (
                    subprocess.check_output(
                        ["netsh", "wlan", "show", "profile", i, "key=clear"]
                    )
                    .decode("utf-8", errors="backslashreplace")
                    .split("\r\n")
                )
                results = [
                    b.split(":")[1][1:]
                    for b in results
                    if self.lang_vars[self.lang]["profile"] in b
                ]
                try:
                    memchache[i] = "{:<}".format(results[0])
                except IndexError:
                    memchache[i] = ""
            except subprocess.CalledProcessError:
                print("{:<30}|  {:<}".format(i, "ENCODING ERROR"))
        return memchache


class Program:
    def __init__(self, lang):
        self.storage = Storage()
        self.profiler = Profiler(lang)

    def run(self):
        self.storage.bulk_storage_update(self.profiler.get_passwords_from_profiles())
        return self.storage

    def export(self, type):
        if type == "cli":
            return str(self.storage)
        else:
            return program.storage.export(type)


if __name__ == "__main__":

    # Available locations
    locations = ["pt_BR"]
    language = locale.getdefaultlocale()[0]

    # Check OS
    if os.name != "nt":
        sys.exit(">> Your OS is not supported. Windows only. (%s)" % os.name)

    # Check Location
    if not language in locations:
        sys.exit(">> Your OS Language is not supported (%s)" % language)

    # CLI
    parser = argparse.ArgumentParser(
        prog="WLAN PROFILES",
        description="Get all WLAN Profiles and passwords stored on OS (MS Windows only)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output options",
        type=str,
        choices=["cli", "json", "txt"],
        default="cli",
    )
    args = parser.parse_args()

    # Main program
    program = Program(language)
    program.run()
    sys.exit(">> " + program.export(args.output))
