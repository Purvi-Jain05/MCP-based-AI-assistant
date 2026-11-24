class ObservationMemory:

    def __init__(self):

        self.history = []

    def add(
        self,
        observation
    ):

        self.history.append(
            observation
        )

    def get_all(
        self
    ):

        return self.history

    def reset(
        self
    ):

        self.history = []