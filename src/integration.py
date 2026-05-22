import numpy as np
import moderngl
import src.settings as settings


def draw_LRAM(ctx, program, func, integration_samples, lower_bound, upper_bound):
    dx = (upper_bound - lower_bound) / integration_samples

    x_starts = np.linspace(lower_bound, upper_bound - dx, integration_samples)
    x_ends   = x_starts + dx
    # Evaluate at the start of the interval
    y_tops   = func(x_starts)
    y_bottom = 0 

    x_starts_ndc  = settings.to_ndc_x(x_starts)
    x_ends_ndc    = settings.to_ndc_x(x_ends)
    y_tops_ndc    = settings.to_ndc_y(y_tops)
    y_bottoms_ndc = settings.to_ndc_y(y_bottom)

    rects = np.zeros((integration_samples, 12), dtype="f4")

    # Triangle 1
    rects[:, 0], rects[:, 1]   = x_starts_ndc, y_bottoms_ndc
    rects[:, 2], rects[:, 3]   = x_ends_ndc, y_bottoms_ndc
    rects[:, 4], rects[:, 5]   = x_starts_ndc, y_tops_ndc

    # Triangle 2
    rects[:, 6], rects[:, 7]   = x_starts_ndc, y_tops_ndc
    rects[:, 8], rects[:, 9]   = x_ends_ndc, y_tops_ndc
    rects[:, 10], rects[:, 11] = x_ends_ndc, y_bottoms_ndc

    vbo = ctx.buffer(rects.tobytes())
    vao = ctx.vertex_array(program, [(vbo, "2f", "in_vert")])
    vao.render(moderngl.TRIANGLES)

    vbo.release()
    vao.release()


def draw_RRAM(ctx, program, func, integration_samples, lower_bound, upper_bound):
    dx = (upper_bound - lower_bound) / integration_samples

    x_starts = np.linspace(lower_bound, upper_bound - dx, integration_samples)
    x_ends   = x_starts + dx
    # Evaluate at the end of the interval
    y_tops   = func(x_ends)
    y_bottom = 0

    x_starts_ndc  = settings.to_ndc_x(x_starts)
    x_ends_ndc    = settings.to_ndc_x(x_ends)
    y_tops_ndc    = settings.to_ndc_y(y_tops)
    y_bottoms_ndc = settings.to_ndc_y(y_bottom)

    rects = np.zeros((integration_samples, 12), dtype="f4")

    # Triangle 1
    rects[:, 0], rects[:, 1]   = x_starts_ndc, y_bottoms_ndc
    rects[:, 2], rects[:, 3]   = x_ends_ndc, y_bottoms_ndc
    rects[:, 4], rects[:, 5]   = x_starts_ndc, y_tops_ndc
    
    # Triangle 2
    rects[:, 6], rects[:, 7]   = x_starts_ndc, y_tops_ndc
    rects[:, 8], rects[:, 9]   = x_ends_ndc, y_tops_ndc
    rects[:, 10], rects[:, 11] = x_ends_ndc, y_bottoms_ndc

    vbo = ctx.buffer(rects.tobytes())
    vao = ctx.vertex_array(program, [(vbo, "2f", "in_vert")])
    vao.render(moderngl.TRIANGLES)

    vbo.release()
    vao.release()


def draw_MRAM(ctx, program, func, integration_samples, lower_bound, upper_bound):
    dx = (upper_bound - lower_bound) / integration_samples

    x_starts = np.linspace(lower_bound, upper_bound - dx, integration_samples)
    x_ends   = x_starts + dx
    x_mids   = x_starts + (dx / 2)
    # Evaluate at the middle of the interval
    y_tops   = func(x_mids)
    y_bottom = 0

    x_starts_ndc  = settings.to_ndc_x(x_starts)
    x_ends_ndc    = settings.to_ndc_x(x_ends)
    y_tops_ndc    = settings.to_ndc_y(y_tops)
    y_bottoms_ndc = settings.to_ndc_y(y_bottom)

    rects = np.zeros((integration_samples, 12), dtype="f4")

    # Triangle 1
    rects[:, 0], rects[:, 1]   = x_starts_ndc, y_bottoms_ndc
    rects[:, 2], rects[:, 3]   = x_ends_ndc, y_bottoms_ndc
    rects[:, 4], rects[:, 5]   = x_starts_ndc, y_tops_ndc

    # Triangle 2
    rects[:, 6], rects[:, 7]   = x_starts_ndc, y_tops_ndc
    rects[:, 8], rects[:, 9]   = x_ends_ndc, y_tops_ndc
    rects[:, 10], rects[:, 11] = x_ends_ndc, y_bottoms_ndc

    vbo = ctx.buffer(rects.tobytes())
    vao = ctx.vertex_array(program, [(vbo, "2f", "in_vert")])
    vao.render(moderngl.TRIANGLES)

    vbo.release()
    vao.release()


def draw_TRAP(ctx, program, func, integration_samples, lower_bound, upper_bound):
    dx = (upper_bound - lower_bound) / integration_samples

    x_starts = np.linspace(lower_bound, upper_bound - dx, integration_samples)
    x_ends   = x_starts + dx
    y_starts = func(x_starts)
    y_ends   = func(x_ends)
    y_bottom = 0

    x_starts_ndc  = settings.to_ndc_x(x_starts)
    x_ends_ndc    = settings.to_ndc_x(x_ends)
    y_starts_ndc  = settings.to_ndc_y(y_starts)
    y_ends_ndc    = settings.to_ndc_y(y_ends)
    y_bottoms_ndc = settings.to_ndc_y(y_bottom)

    rects = np.zeros((integration_samples, 12), dtype="f4")

    # Triangle 1
    rects[:, 0], rects[:, 1]   = x_starts_ndc, y_bottoms_ndc
    rects[:, 2], rects[:, 3]   = x_ends_ndc, y_bottoms_ndc
    rects[:, 4], rects[:, 5]   = x_starts_ndc, y_starts_ndc

    # Triangle 2
    rects[:, 6], rects[:, 7]   = x_starts_ndc, y_starts_ndc
    rects[:, 8], rects[:, 9]   = x_ends_ndc, y_ends_ndc
    rects[:, 10], rects[:, 11] = x_ends_ndc, y_bottoms_ndc

    vbo = ctx.buffer(rects.tobytes())
    vao = ctx.vertex_array(program, [(vbo, "2f", "in_vert")])
    vao.render(moderngl.TRIANGLES)

    vbo.release()
    vao.release()
