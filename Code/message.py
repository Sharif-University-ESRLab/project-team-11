class Message:
    def __init__(self, type: str = None, move_x: int = 0, move_y:int = 0, typed_text: str = None, is_on: bool = False):
        # if it is a message from client:
        # types are: move mouse(move_x, move_y)
        # right click, left click, double click, shut down, restart,
        # keyboard(typed_text)

        # if it is a message from server:
        # types are:
        # Mouse
        # Voice
        # Keyboard
        # Blink
        self.type = type
        self.move_x = move_x
        self.move_y = move_y
        self.typed_text = typed_text
        self.is_on = is_on
