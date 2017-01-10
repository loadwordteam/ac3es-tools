AC3ES Tools
===========

This is a collection of tools for manipulate games files for the game
Ace Combat 3.

The tools are in beta but stable enough for the use.


Requirements
------------

You need Python 3.2 at least with the bitarray library installed.

On Debian based system you can install ``python3-bitarray`` package,
on OpenSuse you should compile it through pip.


Ulz decompressor
----------------

The script ulz.py deflates the ulz files contained in ``ACE.BPB``, it
creates a directory named ``ulz_data``.

You can use it with ``find`` for scan the directories

::
   
    find  unpacked_BPB/ -name '*.ulz' -exec python3 ulz.py {} \;


Contacts
--------

Gianluigi "Infrid" Cusimano <infrid@infrid.com>
http://ac3es.infrid.com/
