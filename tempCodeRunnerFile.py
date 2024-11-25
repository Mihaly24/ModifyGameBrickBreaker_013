    """Check for collisions with the game objects."""
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5  # Center of the ball
        hit_vertical = False  # Flag to check if vertical collision occurred
        hit_horizontal = False  # Flag to check if horizontal collision occurred

        for game_object in game_objects:
            if isinstance(game_object, Paddle):
                paddle_coords = game_object.get_position()
                if (coords[2] >= paddle_coords[0] and coords[0] <= paddle_coords[2] and
                    coords[3] >= paddle_coords[1] and coords[3] <= paddle_coords[3]):
                    # Collision with paddle
                    hit_horizontal = True
                    paddle_center = (paddle_coords[0] + paddle_coords[2]) / 2
                    hit_position = x - paddle_center
                    normalized_hit_position = hit_position / (game_object.width / 2)
                    normalized_hit_position = max(-1, min(1, normalized_hit_position))
                    self.direction[0] = normalized_hit_position
                    self.direction[1] *= -1  # Reverse vertical direction
                    break  # Exit loop after handling paddle collision

            elif isinstance(game_object, Brick):
                if (coords[2] >= game_object.get_position()[0] and coords[0] <= game_object.get_position()[2] and
                    coords[3] >= game_object.get_position()[1] and coords[1] <= game_object.get_position()[3]):
                    # Collision with brick
                    hit_horizontal = True
                    self.direction[1] *= -1  # Reverse the vertical direction
                    game_object.hit()  # Hit the brick
                    break  # Exit loop after handling brick collision

        # Adjust ball's horizontal movement if no vertical collision occurred
        if not hit_horizontal:
            if coords[0] <= 0 or coords[2] >= self.canvas.winfo_width():
                self.direction[0] *= -1  # Reverse horizontal direction if hitting wall