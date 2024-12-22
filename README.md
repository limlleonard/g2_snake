# Snake
## Description
I made the classical game, snake, with python and javascript. In the human mode, you can play the game with left and right key as you have known. In the robot mode, you can see how the reinforcement learning model learn to play the game. Or you can start with a pre-trained model.
![Screenshot of the game](screenshot.png)
## Usage
You can openup the deployed webapp here: (It takes a while to load, expecially for the robot mode.)
https://g2-snake.onrender.com/

(Optional: activate virtual environment)
`git clonse https://github.com/limlleonard/g2_snake`
`cd g2_snake`
`pip install -r requirements.txt`
`python app.py`

## Components
__HTML, CSS and JavaScript__: Frontend

__app.py__: __Flask__ is used to connect frontend and backend. __Thread__ and __Queue__ are used to keep the game running. __SocketIO__ is used to keep sending the position of the snake to the frontend

__game.py__: The game component is to control the snake, place food, control if there is a collission.

__model.py__: __PyTorch__ is used to train the reinforcement learning model by optimizing the quality of action with Bellman equation
## Credit
I learned the PyTorch modeling part from this video:
https://www.youtube.com/watch?v=L8ypSXwyBds&list=PL0I6MJMm4N3sFkA99asXgbKw-IbxuK404&index=10&t=913s