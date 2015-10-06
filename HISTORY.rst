Release History
===============

2.1.0 (2015-10-06)
------------------

**API Changes**

- Frames parsed from binary data now carry a ``body_len`` attribute that
  matches the frame length (minus the frame header).

2.0.0 (2015-09-21)
------------------

**API Changes**

- Attempting to parse unrecognised frames now throws ``ValueError`` instead of
  ``KeyError``.  Thanks to @Kriechi!
- Flags are now validated for correctness, preventing setting flags that
  ``hyperframe`` does not recognise and that would not serialize. Thanks to
  @mhils!
- Frame properties can now be initialized in the constructors. Thanks to @mhils
  and @Kriechi!
- Frames that cannot be sent on a stream now have their stream ID defaulted
  to ``0``. Thanks to @Kriechi!

**Other Changes**

- Frames have a more useful repr. Thanks to @mhils!

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
