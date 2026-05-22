import moderngl
import numpy as np

import settings


def draw_axes(ctx, program):
    origin_x_ndc = settings.to_ndc_x(0)
    origin_y_ndc = settings.to_ndc_y(0)

    axis = np.array([
        # x-axis
        -1.0, origin_y_ndc,
         1.0, origin_y_ndc,
        # y-axis
        origin_x_ndc, -1.0,  
        origin_x_ndc,  1.0,
        ], dtype="f4")

    vbo = ctx.buffer(axis)

    vao = ctx.vertex_array(
        program,
        [(vbo, "2f", "in_vert")]
    )

    vao.render(moderngl.LINES)

    vbo.release()
    vao.release()


def draw_graph(ctx, program, func, graph_samples):
    x_vals = np.linspace(settings.x_min, settings.x_max, graph_samples)
    y_vals = func(x_vals)

    x_vals_ndc = settings.to_ndc_x(x_vals)
    y_vals_ndc = settings.to_ndc_y(y_vals)

    x_start = x_vals_ndc[:-1]
    x_end = x_vals_ndc[1:]

    y_start = y_vals_ndc[:-1]
    y_end = y_vals_ndc[1:]

    graph = np.column_stack([
        x_start, y_start,
        x_end, y_end
    ])

    delta_x = x_end - x_start
    delta_y = np.abs(y_end - y_start)
    slopes = delta_y / delta_x
    
    # Use a threshold to remove large changes in slope
    # (e.g. infinite discontinuities)
    # Note: bugs may occur as the system cannot detect some cases
    # (e.g. jump discontinuities)
    threshold = 1 / delta_x

    mask = (slopes < threshold)
    graph = graph[mask]
    graph = np.real(graph)

    vbo = ctx.buffer(graph.astype("f4").tobytes())

    vao = ctx.vertex_array(
        program,
        [(vbo, "2f", "in_vert")]
    )
    
    vao.render(moderngl.LINES)

    vbo.release()
    vao.release()
