from kivy.animation import Animation

def animate_fade_slide_up(widget):
    # Set initial state
    widget.opacity = 0
    # Store original y or use current y
    original_y = widget.y
    widget.y = original_y - 30

    # Define animation: Fade in and slide up to original position
    anim = Animation(opacity=1, y=original_y, duration=0.6, t='out_quad')
    anim.start(widget)

if __name__ == "__main__":
    print("Result transitions loaded")
