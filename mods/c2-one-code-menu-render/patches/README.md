# C2 ONE-CODE — menu render marker

This is a controlled code-capability experiment. It changes one executable
statement in `Scenes/Menu.gd::render()`:

```text
VersionLabel.text = Constants.GAME_VERSION
  ->
VersionLabel.text = Constants.GAME_VERSION + " [C2-CODE]"
```

The runtime marker is intentionally visible in the live main menu. The test
proves the declared script was compiled, encrypted, loaded, and executed. It
does not prove unrelated gameplay code or persistence behavior.
