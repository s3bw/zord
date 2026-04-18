from zord import Colour, Indicator, Scene, Square


class BinarySearch(Scene):

    def construct(self):
        # Create squares in a row
        squares = []
        square_size = 60  # Slightly smaller squares for 480p
        for i in range(13):
            s = Square(
                label=str(i),
                x=5 + i * 65,  # Adjusted spacing
                y=self.verticle_center(square_size),
                size=square_size,
            )
            squares.append(s)

        # Create arrow indicator
        first_square = squares[0]
        arrow = Indicator(size=15)  # Create indicator without position
        arrow.start_at(first_square)  # Position it properly above the first square

        def shift_arr(sqr):
            sqr.background = Colour.PRIMARY
            arrow.point_at(sqr)
            self.play()
            self.wait(1)
            sqr.background = Colour.BLACK

        # First highlight
        shift_arr(squares[6])
        shift_arr(squares[10])
        shift_arr(squares[8])
        shift_arr(squares[9])
