from zord import Colour, Scene, Square


class TextTransition(Scene):

    background = Colour.BLACK

    def construct(self):

        square_size = 60
        square = Square(
            size=square_size,
            label="Nice!",
            x=self.width // 2 - square_size // 2,  # Center horizontally
            y=self.height // 2 - square_size // 2,  # Center vertically
        )
        self.play()
        self.wait(1)

        square.label = "Hello"
        self.play()
        self.wait(1)


class ServerRequest(Scene):

    background = CustomBackground
    spacing = Spacing.SPACE_AROUND

    def construct(self):

        client = Card(label="client")
        server = Card(label="server")

        arrow = Indicator(style="dotted", animation="sending")
        arrow.point_at(server)
        arrow.point_from(client)

        database = Database(label="postgres")

        arrow = Indicator()
        arrow.point_at(database)
        arrow.point_from(server)


class TextAnimation(Scene):

    def construct(self):

        text = Text("Here is a new wall of text")
