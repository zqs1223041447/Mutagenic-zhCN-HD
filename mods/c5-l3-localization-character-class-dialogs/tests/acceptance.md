# C5-L3 acceptance boundary

Machine acceptance requires:

- the original fingerprint, raw manifest, tool lock, localization-unit hash, and C5-L3 manifest hash are recorded;
- all four source units are locked as `DISPLAY_SAFE` with exact raw-file preimages;
- the generated pack starts from `03_raw` and changes only the two declared scene files plus the cumulative C5-L2 paths and CJK font overlay;
- scene structural token collections remain unchanged;
- the PCK has 3744 entries and no rejected checksum mismatch;
- the EXE is embedded from a fresh copy of `00_original` and round-trips to the intended pack tree;
- the real game window boots without an ALERT or fatal project-load marker.

The phase checkpoint records the C5-L3 character-class dialog scope. It is not
an active blocker for unrelated machine-verifiable work.
