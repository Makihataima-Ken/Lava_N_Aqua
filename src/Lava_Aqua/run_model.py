from src.Lava_Aqua.agents.dqn_agent import DQNAgent
from src.Lava_Aqua.controllers.rl_controller import RLController
from src.Lava_Aqua.core.game import GameLogic

env = GameLogic()

env.load_level(1)

width, height = env.get_grid_dimensions()
agent = DQNAgent(
    state_shape=(width, height, 6),
    gamma=0.99,
    learning_rate=1e-3,
    epsilon_decay=0.995
)

# agent = DQNAgent.load("C:\\Users\\ahmad\\Developement\\Lava_and_Aqua\\assets\\trained models\\dqn_agent_kaggle.pkl")

controller = RLController(
    game_logic=env,
    agent=agent,
    # visualize=False
)

controller.run_level(agent_path="C:\\Users\\ahmad\\Developement\\Lava_and_Aqua\\assets\\trained models\\dqn_agent_kaggle.pkl",visualize=True)

