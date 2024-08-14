class FakeButton:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def update(self, new_state=None) -> None:
        pass

    @property
    def long_press(self) -> bool:
        """Return whether a long press has occured at the last update."""
        return False

    @property
    def short_count(self) -> int:
        """Return the number of short press if a series of short presses has
        ended at the last update."""
        return 0

    @property
    def pressed(self) -> bool:
        """Return whether the button was pressed or not at the last update."""
        return False
