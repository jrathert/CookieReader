# CookieReader

## About this tool

Sometimes, your might be interested in the cookies stored by your browser, _without actually starting it_. 
Consider, e.g., you are a software developer and want to re-use a session key or a JSON Web Token (JWT, 
see https://jwt.io) similar. 

Of course, all browsers today support looking at the content of the cookie store (at least by using developer 
console / inspectors), but sometimes it is just more handy to retrieve these values _on the console_ or in a file.

This small tool, developed in Python, allows to read the cookies from **Google Chrome** as well as **Mozilla Firefox** and
prints them on the console in a (very simple) JSON-like format. It tries to identify/guess the proper location of
your browsers' cookie store (both browsers store cookies in simple SQLite database files) and can be asked to 
only print cookies from specific hosts/domains.

## Limitations

Right now, the script is working on the _Linux OS_ only. Main reason for that is that Chrome encrypts the cookie 
values in its cookie store, and decrypting them requires access to the user's password/key.  Both aspects - the 
decryption and the key access - are to some extent OS-specific. However, it is possible, as some of the code I
leveraged is actually taken from other examples running on MS Windows or mentioning differences in Mac OS X.

That said: Reading the Mozilla Firefox cookies might work out of the box on Mac OS as well as MS Windows by
specifying the path to the DB on the command line (the heuristic to determine the database location will most
likely NOT work on these OS'es).

## Installation

The tool depends on Python 3(.7) and leverages some third party libraries (namely 
[PyCrpyto](https://pypi.org/project/pycrypto/) and [SecretStorage](https://pypi.org/project/SecretStorage/)). 
I use [pipenv](https://pipenv.pypa.io/) to manage these dependencies, so you have two options after downloading 
the source/cloning the repository. 
- Either your OS / Linux distribution already contains the libraries mentioned. Then the tool should work 
  out-of-the-box
- Or you create a pipenv environment:
  ```
      git clone https://github.com/jrathert/cookiereader.it
      cd cookiereader
      pipenv install 
      pipenv run cookiereader.py -h
      ...
  ```

## Usage

Best is to simply call the integrated help
```
Usage: cookiereader.py chrome|firefox [-f cookie_file] [ host(s) ]
  chrome|firefox : mandatory, specify what browser cookies you want to read
  -f cookie_file : optional, specify file to read (needed, if program cannot determine file
  host(s)        : optional, list of hosts/host patterns for which you want to see cookies
Examples:
  # list all cookies from firefox default cookie DB
  $ python cookiereader.py firefox 
  # list cookies from specified firefox cookie DB
  $ python cookiereader.py firefox -f /home/joe/.mozilla/Profile/cookies.sqlite
  # list all chrome cookies from www.microsoft.com or www.facebook.com
  $ python cookiereader.py chrome www.microsoft.com www.facebook.com
  # list cookies stored by *.apple.com domains in specified chrome cookie DB
  $ python cookiereader.py chrome -f /tmp/Cookies %.apple.com
```
For the host specification, the tool supports SQL wildcards, i.e., specifically the '%' sign. See example above.

Output of the tool is a (very) simple JSON format

```
$ python cookiereader.py chrome %.apple.com
{
    "pxro": "1",
    "foo": "bar",
    "as_uct": "2",
    "POD": "de~de",
    "as_dc": "nc",
    #...
    "dssf": "1",
}
$ _
```

## License

### MIT License

Copyright (c) 2021 Jonas Rathert

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

## ToDos

- Some more/better error handling
- Supporting other OS'es (Mac OS, MS Windows)
- Check if all Chromium-based browsers (e.g., MS Edge) can be supported

## Thanks!

I am by no means a professional programmer, and a lot of what I did here was more "compiling other people's 
ideas/code snippets". The source code mentions some of these sources. Thank you. 

