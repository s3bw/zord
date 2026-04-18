from zord import Colour, Group, Rect, Scene, Text


class ChessBoardKnight(Scene):

    background = None

    def construct(self):
        self.width
        size = 30
        gap = 5
        start_x = (self.width - (8 * size + gap * 8)) / 10
        start_y = 80

        board = []
        group = Group()
        for x in range(8):
            row = []
            for y in range(8):
                s = Rect(
                    h=size,
                    w=size,
                    x=start_x + x * (size + gap),
                    y=start_y + y * (size + gap),
                )
                row.append(s)
                group.append(s)
            board.append(row)

        board[1][4].background = Colour.ACCENT
        board[3][4].background = Colour.ACCENT
        board[4][2].background = Colour.ACCENT
        board[6][6].background = Colour.ACCENT

        board[4][4].background = Colour.BASE
        Text("Mask", 10, 80 + 35 * 8 + 30, _temporary=True)

        self.play()
        self.wait(1)
        exit()

        posx, posy = 4, 4

        for i in range(8):
            board[(posx + i) % 8][posy].background = Colour.PRIMARY
            board[posx][(posy + i) % 8].background = Colour.PRIMARY
            board[4][4].background = Colour.BASE

        self.play()
        self.wait(1)

        for i in range(8):
            board[(posx + i) % 8][posy].background = Colour.WHITE
            board[posx][(posy + i) % 8].background = Colour.WHITE
            board[4][4].background = Colour.BASE

        board[1][4].background = Colour.SHINY
        board[3][4].background = Colour.SHINY
        board[4][2].background = Colour.SHINY

        self.play()
        self.wait(1)

        square1 = board[1][4]
        square2 = board[3][4]
        square3 = board[4][2]

        square1.x = board[7][0].x + gap + size + 50
        square2.x = square1.x
        square3.x = square2.x

        square1.y = board[7][0].y
        square2.y = square1.y + size + gap
        square3.y = square2.y + size + gap

        self.play()
        self.wait(1)

        self.play()
        self.wait(1)

        # Scale the board up by 1.5x
        # newgroup = group.copy()
        # newgroup.move(x=160, y=100)
        # newgroup.scale(factor=0.5)
        # self.play()
        # self.wait(1)
