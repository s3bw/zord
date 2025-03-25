from zord import Scene, Square, Indicator, Colour

class BinarySearch(Scene):

    background = None

    def construct(self):
        # Create squares in a row
        squares = []
        square_size = 40  # Slightly smaller squares for 480p
        for i in range(17):
            s = Square(
                label=str(i), 
                x=40 + i*45,  # Adjusted spacing
                y=self.height//2 - square_size//2,  # Center vertically
                size=square_size
            )
            squares.append(s)
        
        # Create arrow indicator
        arrow = Indicator(size=15)  # Slightly smaller arrow

        # First highlight
        squares[7].background = Colour.BLUE
        arrow.point_at(squares[7])
        self.play()
        self.wait(1)

        # Second highlight
        squares[7].background = Colour.GRAY
        arrow.point_at(squares[13])
        squares[13].background = Colour.BLUE
        self.play()
        self.wait(1)

        # Third highlight
        squares[13].background = Colour.GRAY
        arrow.point_at(squares[9])
        squares[9].background = Colour.BLUE
        self.play()
        self.wait(1)

        # Fourth highlight
        squares[9].background = Colour.GRAY
        arrow.point_at(squares[10])
        squares[10].background = Colour.BLUE
        self.play()
        self.wait(1)