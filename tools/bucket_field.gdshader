// Paint Loop bucket — data-driven shading field (v22 field pipeline)
// Идея: цвет ведра = f(world_z_norm, normal_z). Таблица 24×10 снята со скриншотов рефа
// через /tmp/v22_field.py (бин-медианы выровненных пикселей). В Godot: ImageTexture 24×10.
//
// Использование:
//   var img = Image.create_from_data(24, 10, false, Image.FORMAT_RGB8, bytes)
//   var tex = ImageTexture.create_from_image(img)
//   material.set_shader_parameter("field_tex", tex)
shader_type spatial;
render_mode unshaded; // игра использует плоскую заливку/градиент; свет не нужен

uniform sampler2D field_tex : filter_linear, repeat_disable;
uniform float z_min = 0.0;   // мировая высота низа ведра (поза-зависимо)
uniform float z_max = 0.9;   // мировая высота верха

void fragment() {
    float zn = clamp((WORLD_MATRIX[3][1] - z_min) / (z_max - z_min), 0.0, 0.0); // заглушка: заполняется вершинным полем
    // Вершинный вариант: передайте world-z и normal-z через varying
    float nz = clamp(NORMAL[1] * 0.5 + 0.5, 0.0, 1.0);
    vec2 uv = vec2(nz, zn);
    vec3 col = texture(field_tex, uv).rgb;
    ALBEDO = col;
}
