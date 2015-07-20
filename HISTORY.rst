Release History
===============

1.1.1 (2015-07-20)
------------------

- Fix a bug where ``FRAME_MAX_LEN`` was one byte too small.

1.1.0 (2015-06-28)
------------------

- Add ``body_len`` property to frames to enable introspection of the actual
  frame length. Thanks to @jdecuyper!

1.0.1 (2015-06-27)
------------------

- Fix bug where the frame header would have an incorrect length added to it.

1.0.0 (2015-04-12)
------------------

- Initial extraction from `hyper`_.

.. _hyper: http://hyper.readthedocs.org/
