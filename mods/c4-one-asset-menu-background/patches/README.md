# C4 ONE-ASSET — menu background cache

This is a controlled asset-capability experiment. It replaces exactly one
runtime texture cache file:

```text
res://.import/background_blurred.png-2b6b19973a497aee4145e7f6c132790d.stex
  <- existing 960x536 background.png STEX cache
```

The target path and the `background_blurred.png.import` metadata are preserved.
The replacement is deliberately sourced from an existing, same-dimension
Godot 3 STEX/WebP asset because no locked Godot editor/importer is available in
the project toolchain. This proves runtime asset overlay and import-path
preservation; it does not prove a fresh source-PNG reimport.
