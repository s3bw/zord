from zord import Colour, Group, Rect, Scene


class ChessBoardKnight(Scene):

    background = None

    def construct(self):
        size = 30

        board = []
        group = Group()
        for x in range(8):
            row = []
            for y in range(8):
                s = Rect(
                    h=size,
                    w=size,
                    x=160 + x * (size + 5),
                    y=60 + y * (size + 5),
                )
                row.append(s)
                group.append(s)
            board.append(row)

        self.play()
        self.wait(1)

        board[4][4].background = Colour.ACCENT
        board[3][2].background = Colour.PRIMARY
        board[2][3].background = Colour.PRIMARY
        board[5][6].background = Colour.PRIMARY
        self.play()
        self.wait(1)

        # Scale the board up by 1.5x
        newgroup = group.copy()
        newgroup.move(x=160, y=100)
        newgroup.scale(factor=0.5)
        self.play()
        self.wait(1)
