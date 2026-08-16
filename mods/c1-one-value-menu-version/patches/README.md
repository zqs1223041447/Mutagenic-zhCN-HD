# C1 ONE-VALUE — menu version display

This is a controlled capability experiment. It changes exactly one display value:

```text
Constants.GAME_VERSION: EA 0.6.2 -> EA 0.6.2 [C1-VALUE]
```

The value is rendered by `Scenes/Menu.gd` into the main-menu `VersionLabel`.
The experiment does not change gameplay data, scenes, assets, Steam behavior, or
the menu event flow. The runtime-specific check is a short visual check of the
main-menu Build label after boot.
