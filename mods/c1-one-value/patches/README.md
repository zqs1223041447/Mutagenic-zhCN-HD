# C1 one-value patch

The executable patch is declared in `../mod.json` and is guarded by the
preimage SHA-256 of the clean recovered source. It changes exactly one runtime
class default: `AreaSkillEffect.radius`, `15.0` to `16.0`.

This patch intentionally does not modify a scene path, node name, resource
reference, translation string, or unrelated script.
