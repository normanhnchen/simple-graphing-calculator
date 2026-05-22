#version 330

out vec4 fragColor;

uniform vec4 in_color;
uniform vec2 grid_spacing;

void main() {
    fragColor = in_color;
}