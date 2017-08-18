AC3ES Tools
===========

This is a collection of tools for manipulate games files for the game
Ace Combat 3.

It has a full working Ulz compressor/decompressor.


Requirements
------------

You need Python >= 3.2

Usage
-----

The tool has two sub commands, the *ulz* command for compress/decompress files
and *info* for get details about the ulz and the known iso or bpb of the game.

..

    usage: ac3es.py [-h] {ulz,info} ...
    
    positional arguments:
      {ulz,info}  Commands
        ulz       Manipulate ulz files
        info      Check files
    
    optional arguments:
      -h, --help  show this help message and exit
    

..

    usage: ac3es.py ulz [-h] [--compress FILE] [--ulz-type {0,2}]
                        [--level {1,2,4,8}] [--store-only] [--like-file LIKE_FILE]
                        [--decompress ULZ] [--output-file FILE] [--parents]
                        [--keep]
    
    optional arguments:
      -h, --help            show this help message and exit
      --compress FILE, -c FILE
                            Compress the file in ulz
      --decompress ULZ, -d ULZ
                            decompress the file in the current directory
      --output-file FILE, -f FILE
                            override output filename
      --parents, -p         Create directories for destination files if they don't
                            exists
      --keep, -k            prompt before every removal or destructive change
    
    compression:
      --ulz-type {0,2}      Define the ulz version to use
      --level {1,2,4,8}, -l {1,2,4,8}
                            Compression levels 1/2/4/8 uses a search buffer
                            1024/2048/4096/8192 bytes long.
      --store-only, -s      Store data on ulz file, needs anyway a compression
                            level
      --like-file LIKE_FILE
                            Get compression parameters from file
    

.. 

    usage: ac3es.py info [-h] FILES [FILES ...]
    
    positional arguments:
      FILES       One or more file to get info
    
    optional arguments:
      -h, --help  show this help message and exit
    
    

Examples
^^^^^^^^

Compress an image and put the output into the same directory

..

    ac3es.py ulz --compress image.tim --ulz-type=2 --level=1

or define another destination

..

    ac3es.py ulz --compress jap_0002.tim --ulz-type=2 --level=1 --output-file=mycompress.ulz

Get what parameters use from the original file

..

    ac3es.py info BPB/0386/0001/0000.ulz

More parameters are avaible, just type help for the sub command

..

    ac3es.py ulz --help
    ac3es.py info --help


Contacts
--------

Gianluigi "Infrid" Cusimano <infrid@infrid.com>
http://ac3es.infrid.com/
