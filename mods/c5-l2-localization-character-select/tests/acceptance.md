# C5-L2 acceptance boundary

Must pass before any human visual request:

- original fingerprint, raw manifest, tool lock, and localization-unit hashes match the experiment;
- all four source files/units pass exact preimage and `DISPLAY_SAFE` checks;
- only the declared `Scenes/Menu.tscn`, `Scenes/Popups/Dialogs/CharacterSelect/CharacterSelect.tscn`, and `Fonts/rsans.ttf` logical paths change;
- scene structural token collections remain unchanged outside the three `text` fields;
- the PCK has 3744 entries with valid checksums;
- the fresh original EXE has valid embedded PCK/PE metadata and roundtrip extraction;
- the real game window boots without an ALERT or fatal project-load marker.

The machine Gate does not prove character-selection interaction or visual
quality. Those remain separate runtime/human evidence requirements.
