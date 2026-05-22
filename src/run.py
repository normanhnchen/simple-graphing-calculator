import pygame
import moderngl
import os
import sympy as sp

import src.settings as settings
from src.graph import *
from src.integration import *
from src.calc import *


def init_window():
    global ctx, program

    pygame.init()

    pygame.display.set_caption("Graph")

    screen = pygame.display.set_mode(settings.resolution, pygame.OPENGL | pygame.DOUBLEBUF)

    ctx = moderngl.create_context()
    ctx.viewport = (0, 0, settings.resolution[0], settings.resolution[1])
    ctx.enable(moderngl.LINEAR_MIPMAP_LINEAR)
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
    global ctx, program
    global integration_samples
    global lower_bound, upper_bound

    clock = pygame.time.Clock()
    FPS = 60

    # Type of integration estimation method drawn
    # (LRAM, RRAM, MRAM, TRAP)
    integration_type = "LRAM"
    # Number of samples used for integration under the graph
    integration_samples = 8192
    # Number of samples used to draw the graph
    # Note: There is no option to change this during runtime
    graph_samples = 8192
    # Default bounds of integration
    lower_bound = -5
    upper_bound = 5
    # How fast the bounds expand/shrink/shifts when pressing associated keys during runtime
    bound_exp_factor = 0.5
    
    # Clear the console
    os.system("cls" if os.name == "nt" else "clear")
    print_controls()

    dragging = False
    running = True

    while running:
        # Set FPS
        clock.tick(FPS)
        
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
            
            elif event.type == pygame.MOUSEWHEEL:
                # Zoom in
                if event.y > 0:
                    settings.x_min /= 1.1
                    settings.x_max /= 1.1
                    settings.y_min /= 1.1
                    settings.y_max /= 1.1
                
                # Zoom out
                elif event.y < 0:
                    settings.x_min *= 1.1
                    settings.x_max *= 1.1
                    settings.y_min *= 1.1
                    settings.y_max *= 1.1
                
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
        integration_samples = max(1, min(integration_samples, 262144))
        
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
    while True:
        print(
            "\nPlease print a function to be drawn on screen.\n"
            "Print \"help\" for function syntax help/rules."
        )
        user_input = input()

        if user_input.lower().strip() == "help":
            print_syntax_help()
            continue

        return user_input


def make_function(user_input):
    x = sp.Symbol("x")

    expr = sp.parse_expr(user_input)

    num_func = sp.lambdify(x, expr, modules=["numpy"])

    def func(x):
        # Set x to dtype "complex" to prevent complex value errors
        x = np.array(x, dtype=complex)

        # Ignore all math errors to prevent errors from stopping the program
        # Discard invalid values later
        with np.errstate(all="ignore"):
            res = num_func(x)
            # Check if the original number was negative and complex
            # If the number was negative and complex, get the negative magnitude of the complex number
            # Otherwise, get the real number
            res = np.where(np.iscomplex(res) & (np.real(x) < 0), -np.abs(res), np.real(res))
            # Return the invalid values as NaN to prevent drawing on screen
            res = np.where(np.isreal(res), np.real(res), np.nan)
            
            return res
            
    return func


def print_syntax_help():
    print(
        "\n--- Function Syntax ---\n"
        "Use variable: x\n"
        "Operators: +, -, *, /, **\n"
        "Functions: sin, cos, tan, sqrt, ln, log, exp\n"
        "Constants: pi, e\n"
        "Example: sin(10*x) + sqrt(x**2) - tan(1/x)\n"
    )



def print_controls():
    print(
        "--- Controls ---\n"
        "Press 1: Draw Left Riemann Approximation\n"
        "Press 2: Draw Right Riemann Approximation\n"
        "Press 3: Draw Midpoint Riemann Approximation\n"
        "Press 4: Draw Trapezoidal Approximation\n"
        "Press [: Decrease Integration Samples by a factor of 2\n"
        "Press ]: Increase Integration Samples by a factor 2\n"
        "Press o: Print the integration approximations\n"
        "Press ←: Shift integration bounds left\n"
        "Press →: Shift integration bounds right\n"
        "Press ↓: Shift the upper integration bound left\n"
        "Press ↑: Shift the upper integration bound right\n"
        "Press r: Reset settings to its default values"
    )


def print_integrals():
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
    global lower_bound, upper_bound

    settings.window_scale = 10

    settings.x_min = -settings.window_scale
    settings.x_max =  settings.window_scale
    settings.y_min = -settings.window_scale
    settings.y_max =  settings.window_scale

    lower_bound = -5
    upper_bound =  5


def main():
    global func

    func = make_function(input_func())
    init_window()
    run()


if __name__ == "__main__":
    main()
