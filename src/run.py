import pygame
import moderngl
import os
import sympy as sp
import numpy as np

import src.settings as settings
from src.graph import *
from src.integration import *
from src.calc import *


def init_window():
    """Initialize the window and OpenGL context."""

    global ctx, program

    pygame.init()

    pygame.display.set_caption("Graph")

    screen = pygame.display.set_mode(settings.resolution, pygame.OPENGL | pygame.DOUBLEBUF)

    ctx = moderngl.create_context()
    ctx.viewport = (0, 0, settings.resolution[0], settings.resolution[1])
    # Allow for transparency
    ctx.enable(moderngl.BLEND)

    with open("src/draw.vs", "r") as f:
        vertex_source = f.read()
    with open("src/draw.fs", "r") as f:
        fragment_source = f.read()

    program = ctx.program(
        vertex_source, fragment_source
    )


def run():
    """Main loop of the program. Handles events and drawing on screen."""

    global ctx, program
    global integration_samples
    global lower_bound, upper_bound

    clock = pygame.time.Clock()

    integration_type = settings.DEFAULT_INTEGRATION_TYPE
    integration_samples = settings.DEFAULT_INTEGRATION_SAMPLES
    graph_samples = settings.GRAPH_SAMPLES
    lower_bound = settings.DEFAULT_LOWER_BOUND
    upper_bound = settings.DEFAULT_UPPER_BOUND
    bound_exp_factor = settings.BOUND_EXP_FACTOR
    
    # Clear the console
    os.system("cls" if os.name == "nt" else "clear")
    print_controls()

    dragging = False
    running = True

    while running:
        # Set FPS
        clock.tick(settings.FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    integration_type = "LRAM"
                elif event.key == pygame.K_2:
                    integration_type = "RRAM"
                elif event.key == pygame.K_3:
                    integration_type = "MRAM"
                elif event.key == pygame.K_4:
                    integration_type = "TRAP"
                elif event.key == pygame.K_LEFTBRACKET:
                    integration_samples //= 2
                elif event.key == pygame.K_RIGHTBRACKET:
                    integration_samples *= 2
                elif event.key == pygame.K_LEFT:
                    lower_bound -= bound_exp_factor
                    upper_bound -= bound_exp_factor
                elif event.key == pygame.K_RIGHT:
                    lower_bound += bound_exp_factor
                    upper_bound += bound_exp_factor
                elif event.key == pygame.K_DOWN:
                    upper_bound -= bound_exp_factor
                elif event.key == pygame.K_UP:
                    upper_bound += bound_exp_factor
                elif event.key == pygame.K_o:
                    # Clear the console
                    os.system("cls" if os.name == "nt" else "clear")
                    print_controls()
                    print_integrals()
                elif event.key == pygame.K_r:
                    default_settings()
            
            # Zoom in/out with mouse wheel, centered on the mouse position
            elif event.type == pygame.MOUSEWHEEL:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                current_width = settings.x_max - settings.x_min
                current_height = settings.y_max - settings.y_min

                world_x = settings.x_min + (mouse_x / settings.resolution[0]) * current_width
                world_y = settings.y_max - (mouse_y / settings.resolution[1]) * current_height

                # Zoom in/out depending if the mouse wheel is scrolled up or down
                scale = 1 / 1.1 if event.y > 0 else 1.1

                # Set new bounds
                settings.x_min = world_x - (world_x - settings.x_min) * scale
                settings.x_max = world_x + (settings.x_max - world_x) * scale
                settings.y_min = world_y - (world_y - settings.y_min) * scale
                settings.y_max = world_y + (settings.y_max - world_y) * scale
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    dragging = True

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            
            elif event.type == pygame.MOUSEMOTION and dragging:
                rel_x, rel_y = event.rel

                # Calculate the width/height shown on screen (in math coordinates)
                current_width = settings.x_max - settings.x_min
                current_height = settings.y_max - settings.y_min
                
                dx = (rel_x / settings.resolution[0]) * current_width
                dy = (rel_y / settings.resolution[1]) * current_height

                # Add/subtract to make dragging feel more "natural"
                settings.x_min -= dx
                settings.x_max -= dx
                settings.y_min += dy
                settings.y_max += dy


        # Clip the integration samples to bounds
        # (to prevent issues and to prevent lagging out)
        integration_samples = max(settings.MIN_INTEGRATION_SAMPLES, min(integration_samples, settings.MAX_INTEGRATION_SAMPLES))
        
        ctx.clear(1.0, 1.0, 1.0)

        program["in_color"] = np.array([0, 0, 0, 1.0], dtype="f4")
        draw_axes(ctx, program)
        program["in_color"] = np.array([0, 0, 0, 1.0], dtype="f4")
        draw_graph(ctx, program, func, graph_samples)

        if lower_bound < upper_bound:
            # Draw red when the lower bound is less than the upper bound
            program["in_color"] = np.array([1, 0, 0, 0.5], dtype="f4")
        else:
            # Draw blue when the lower bound is greater than the upper bound
            program["in_color"] = np.array([0, 0, 1, 0.5], dtype="f4")
        if integration_type == "LRAM":
            draw_LRAM(ctx, program, func, integration_samples, lower_bound, upper_bound)
        elif integration_type == "RRAM":
            draw_RRAM(ctx, program, func, integration_samples, lower_bound, upper_bound)
        elif integration_type == "MRAM":
            draw_MRAM(ctx, program, func, integration_samples, lower_bound, upper_bound)
        elif integration_type == "TRAP":
            draw_TRAP(ctx, program, func, integration_samples, lower_bound, upper_bound)
        
        pygame.display.flip()


def input_func():
    """
    Get user input for the function to be graphed on screen.
    Print syntax help if the user types "help".
    """

    while True:
        print(
            "\nPlease print a function to be drawn on screen.\n"
            "Print \"help\" for function syntax help/rules.\n"
        )
        user_input = input()

        if user_input.lower().strip() == "help":
            print_syntax_help()
            continue

        return user_input


def make_function(user_input):
    """
    Convert the user input string into a function
    that can be evaluated without errors.
    """

    x = sp.Symbol("x")

    expr = sp.parse_expr(user_input)

    num_func = sp.lambdify(x, expr, modules=["numpy"])

    def func(x):
        # Use float inputs so invalid real-domain values become NaN.
        x = np.array(x, dtype=float)

        # Ignore all math errors to prevent errors from stopping the program
        # Discard invalid or complex values later.
        with np.errstate(all="ignore"):
            res = num_func(x)
            if np.iscomplexobj(res):
                res = np.where(np.isreal(res), np.real(res), np.nan)
            else:
                res = np.where(np.isfinite(res), res, np.nan)

            return res

    return func


def print_syntax_help():
    print(
        "\n--- Function Syntax ---\n"
        "This calculator uses SymPy expression syntax.\n"
        "Use the variable: x\n"
        "Operators: +, -, *, /, **, unary -\n"
        "Functions: sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, exp, log, sqrt, abs\n"
        "Constants: pi, E\n"
        "Examples: sin(10*x), sqrt(x**2), log(x), exp(-x**2)\n"
        "You can use any SymPy-parsable expression.\n"
        "For complete syntax and advanced features, see SymPy parser docs:\n"
        "https://docs.sympy.org/latest/modules/parsing.html\n"
    )


def print_controls():
    print(
        "--- Controls ---\n"
        "Press 1: Draw Left Riemann Approximation\n"
        "Press 2: Draw Right Riemann Approximation\n"
        "Press 3: Draw Midpoint Riemann Approximation\n"
        "Press 4: Draw Trapezoidal Approximation\n"
        "Press [: Decrease Integration Samples by a factor of 2\n"
        "Press ]: Increase Integration Samples by a factor of 2\n"
        "Press o: Print the integration approximations\n"
        "Press ←: Shift integration bounds left\n"
        "Press →: Shift integration bounds right\n"
        "Press ↓: Shift the upper integration bound down\n"
        "Press ↑: Shift the upper integration bound up\n"
        "Press r: Reset settings to its default values"
    )


def print_integrals():
    """Calculate and print the integration approximations to the console."""
    global lower_bound, upper_bound, integration_samples

    lram = LRAM(lower_bound, upper_bound, func, integration_samples)
    rram = RRAM(lower_bound, upper_bound, func, integration_samples)
    mram = MRAM(lower_bound, upper_bound, func, integration_samples)
    trap = TRAP(lower_bound, upper_bound, func, integration_samples)

    print(
        "--- Integration Approximations ---\n"
        f"Left Riemann Sum: {lram:.8f}\n"
        f"Right Riemann Sum: {rram:.8f}\n"
        f"Midpoint Riemann Sum: {mram:.8f}\n"
        f"Trapezoidal Rule: {trap:.8f}"
    )


def default_settings():
    """Reset settings to its default values."""

    global lower_bound, upper_bound

    settings.window_scale = settings.DEFAULT_WINDOW_SCALE

    settings.x_min = settings.DEFAULT_X_MIN * settings.window_scale
    settings.x_max = settings.DEFAULT_X_MAX * settings.window_scale
    settings.y_min = settings.DEFAULT_Y_MIN * settings.window_scale
    settings.y_max = settings.DEFAULT_Y_MAX * settings.window_scale

    lower_bound = settings.DEFAULT_LOWER_BOUND
    upper_bound = settings.DEFAULT_UPPER_BOUND


def main():
    """Main function to run the program."""

    global func

    func = make_function(input_func())
    init_window()
    run()


if __name__ == "__main__":
    main()
