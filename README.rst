nametrans
=========

.. image:: https://badge.fury.io/py/nametrans.png
        :target: https://badge.fury.io/py/nametrans

.. image:: https://travis-ci.org/numerodix/nametrans.png?branch=master
    :target: https://travis-ci.org/numerodix/nametrans

.. image:: https://pypip.in/wheel/nametrans/badge.png
    :target: https://pypi.python.org/pypi/nametrans/

.. image:: https://pypip.in/license/nametrans/badge.png
        :target: https://pypi.python.org/pypi/nametrans/


Python version support: CPython 2.6, 2.7, 3.2, 3.3, 3.4 and PyPy.


Installation
------------

.. code:: bash

    $ pip install nametrans
    $ nametrans


Usage
-----


Simple substitutions
^^^^^^^^^^^^^^^^^^^^

The simplest use is just a straight search and replace. All the files in the
current directory will be tried to see if they match the search string.

.. code:: bash

    $ nametrans.py "apple" "orange"
    * I like apple.jpg    -> I like orange.jpg
    * pineapple.jpg       -> pineorange.jpg
    * The best apples.jpg -> The best oranges.jpg
    Rename 3 files? [y/N]


Ignore case
"""""""""""

Matching against strings with different case is easy.

.. code:: bash

    $ nametrans.py -i "pine" "wood"
    * pineapple.jpg -> woodapple.jpg
    * Pinetree.jpg  -> woodtree.jpg
    Rename 3 files? [y/N]


Literal
"""""""

The search string is actually a regular expression. If you use characters that
have a special meaning in regular expressions then set the *literal* option and
it will do a standard search and replace. (If you don't know what regular
expressions are, just use this option always and you'll be fine.)

.. code:: bash

    $ nametrans.py --lit "(1)" "1"
    * funny picture (1).jpg -> funny picture 1.jpg
    Rename 1 files? [y/N]


Root
""""

If you prefer the spelling "oranje" instead of "orange" you can replace the G
with a J. This will also match the extension ".jpg", however. So in a case like
this set the *root* option to consider only the root of the filename for
matching.

.. code:: bash

    $ nametrans.py --root "g" "j"
    * I like orange.jpg    -> I like oranje.jpg
    * pineorange.jpg       -> pineoranje.jpg
    * The best oranges.jpg -> The best oranjes.jpg
    Rename 3 files? [y/N]


Hygienic uses
^^^^^^^^^^^^^

Short of specific cases of transforms, there are some general options that have
to do with maintaining consistency in filenames that can apply to many
scenarios.


Neat
""""

The *neat* option tries to make filenames neater by capitalizing words and
removing characters that are typically noise. It also does some simple sanity
checks like removing spaces or underscores at the ends of the name.

.. code:: bash

    $ nametrans.py --neat
    * _funny___picture_(1).jpg -> Funny - Picture (1).jpg
    * i like apple.jpg         -> I Like Apple.jpg
    * i like peach.jpg         -> I Like Peach.jpg
    * pineapple.jpg            -> Pineapple.jpg
    * the best apples.jpg      -> The Best Apples.jpg
    Rename 5 files? [y/N]


Lower
"""""

If you prefer lowercase, here is the option for you.

.. code:: bash

    $ nametrans.py --lower
    * Funny - Picture (1).jpg -> funny - picture (1).jpg
    * I Like Apple.jpg        -> i like apple.jpg
    * I Like Peach.JPG        -> i like peach.jpg
    * Pineapple.jpg           -> pineapple.jpg
    * The Best Apples.jpg     -> the best apples.jpg
    Rename 5 files? [y/N]

If you want the result of neat and then lowercase, just set them both. (If you
like underscores instead of spaces, also set ``--under``.)


Non-flat uses
^^^^^^^^^^^^^

Assuming the files are named consistently you can throw them into separate
directories by changing some character into the path separator.

**Note:** On Windows, the path separator is ``\`` and you may have to write it
as ``\\\\``.

.. code:: bash

    $ nametrans.py " - " "/"
    * france - nice - seaside.jpg -> france/nice/seaside.jpg
    * italy - rome.jpg            -> italy/rome.jpg
    Rename 2 files? [y/N]

The inverse operation is to *flatten* the entire directory tree so that all the
files are put in the current directory. The empty directories are removed.

.. code:: bash

    $ nametrans.py --flatten
    * france/nice/seaside.jpg -> france - nice - seaside.jpg
    * italy/rome.jpg          -> italy - rome.jpg
    Rename 2 files? [y/N]

In general, the *recursive* option will take all files found recursively and make
them available for substitutions. It can be combined with other options to do
the same thing recursively as would otherwise happen in a single directory.

.. code:: bash

    $ nametrans.py -r --neat 
    * france/nice/seaside.jpg -> France/Nice/Seaside.jpg
    * italy/rome.jpg          -> Italy/Rome.jpg
    Rename 2 files? [y/N]

In recursive mode the whole path will be matched against. You can make sure the
matching only happens against the file part of the path with ``--files`` or only
the directory part with ``--dirs``.


Special uses
^^^^^^^^^^^^

Directory name
""""""""""""""

Sometimes filenames carry no useful information and serve only to maintain them
in a specific order. The typical case is pictures from your camera that have
meaningless sequential names, often with gaps in the sequence where you have
deleted some pictures that didn't turn out well. In this case you might want to
just use the name of the directory to rename all the files sequentially.

.. code:: bash

    $ nametrans.py -r --dirname                                                              
    * rome/DSC00001.jpg -> rome/rome 1.jpg
    * rome/DSC00007.jpg -> rome/rome 2.jpg
    * rome/DSC00037.jpg -> rome/rome 3.jpg
    * rome/DSC00039.jpg -> rome/rome 4.jpg
    Rename 4 files? [y/N]


Rename sequentially
"""""""""""""""""""

Still in the area of sequential names, at times the numbers have either too few
leading zeros to be sorted correctly or too many unnecessary zeros. With this
option you can specify how many leading zeros you want (and if you don't say
how many, it will find out on its own).

.. code:: bash

    $ nametrans.py -r --renseq 1:3                                                           
    * rome/1.jpg   -> rome/001.jpg
    * rome/7.jpg   -> rome/007.jpg
    * rome/14.jpg  -> rome/014.jpg
    * rome/18.jpg  -> rome/018.jpg
    * rome/123.jpg -> rome/123.jpg
    Rename 5 files? [y/N]

The argument required here means ``field:width``, so in a name like:

    series14_angle3_shot045.jpg

the number ``045`` can be shortened to ``45`` with ``3:2`` (third field from
the beginning) or ``-1:2`` (first field from the end).
