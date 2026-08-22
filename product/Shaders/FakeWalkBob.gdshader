shader_type canvas_item;
// FakeWalkBob — shader 版本（与 FakeWalkBob.gd 互为替代）
// 用法：在 AnimatedSprite2D / Sprite2D 的 material 上挂载此 shader，
// walk_speed > 0 时产生 position:y ±1px + scale 微缩放；静止时归零。
// 与真帧兼容：真帧落地后仅需 AnimatedSprite2D.play("walk")，此 shader 可保留或移除，
// 因 walk 帧本身已含位移，shader 的 1px bob 会成为额外细微抖动，不冲突。
// 若需完全禁用 shader 走路，可将 walk_speed 设为 0。

uniform float walk_speed : hint_range(0.0, 20.0) = 0.0;
uniform float bob_amplitude : hint_range(0.0, 4.0) = 1.0;
uniform float scale_amplitude : hint_range(0.0, 0.1) = 0.02;

void vertex() {
	// 周期 0.24s ≈ 4.166 Hz -> 角频率 2*PI / 0.24
	float freq = 6.2831853 / 0.24; // 26.1799
	float t = TIME * max(walk_speed, 0.0) * 0.18; // walk_speed 调制，阈值外由脚本驱动 walk_speed uniform
	// 若 walk_speed == 0 则无位移
	if (walk_speed > 0.5) {
		float s = sin(TIME * freq);
		// 1px 在 canvas_item 中约为 1.0 像素偏移（受 zoom 影响，但保持 1px 量级）
		VERTEX.y += s * bob_amplitude;
		// 微缩放：以纹理中心为锚点缩放
		float sc = 1.0 + s * scale_amplitude * 0.5;
		VERTEX *= sc;
	}
}

// 可选：在 _physics_process 中根据 velocity.length()>10 驱动：
//   material.set_shader_parameter("walk_speed", velocity.length() / 100.0 * 10.0)
// 或 material.set_shader_parameter("walk_speed", moving ? 10.0 : 0.0)
