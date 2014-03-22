nametrans
=========

.. image:: https://badge.fury.io/py/nametrans.png
        :target: https://badge.fury.io/py/nametrans

.. image:: https://travis-ci.org/numerodix/nametrans.png?branch=master
    :target: https://travis-ci.org/numerodix/nametrans


Install
-------

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

Matching against strings with different case is easy.

.. code:: bash

    $ nametrans.py -i "pine" "wood"
    * pineapple.jpg -> woodapple.jpg
    * Pinetree.jpg  -> woodtree.jpg
    Rename 3 files? [y/N]

The search string is actually a regular expression. If you use characters that
have a special meaning in regular expressions then set the *literal* option and
it will do a standard search and replace. (If you don't know what regular
expressions are, just use this option always and you'll be fine.)

.. code:: bash

    $ nametrans.py --lit "(1)" "1"
    * funny picture (1).jpg -> funny picture 1.jpg
    Rename 1 files? [y/N]

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

The *neat* option tries to make filenames neater by capitalizing words and
removing characters that are typically junk. It also does some simple sanity
checks like removing spaces or underscores at the ends of the name.

.. code:: bash

    $ nametrans.py --neat
    * _funny___picture_(1).jpg -> Funny - Picture (1).jpg
    * i like apple.jpg         -> I Like Apple.jpg
    * i like peach.jpg         -> I Like Peach.jpg
    * pineapple.jpg            -> Pineapple.jpg
    * the best apples.jpg      -> The Best Apples.jpg
    Rename 5 files? [y/N]

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
