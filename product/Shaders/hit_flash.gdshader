shader_type canvas_item;
// P4-A R1: white hit flash. Set flash_amount > 0 on hit, tween back to 0.

uniform float flash_amount : hint_range(0.0, 4.0) = 0.0;

void fragment() {
	vec4 base = texture(TEXTURE, UV);
	COLOR = vec4(mix(base.rgb, vec3(1.0), clamp(flash_amount, 0.0, 1.0)), base.a) * COLOR;
}
