import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import pandas as pd 
import numpy as np 

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.valid_light = ['green','red']
        self.valid_action = [None,'left','right','forward']
        self.valid_state = [(light,oncoming,left,right,next_waypoint) for light in self.valid_light \
        for oncoming in self.valid_action for left in self.valid_action for right in self.valid_action \
        for next_waypoint in self.valid_action]
        self.Q = pd.DataFrame(np.random.rand(4,512),columns=self.valid_state,index=self.valid_action)
        self.learningrate = 0.7
        self.randomaction = 0.4
        self.discount = 0.7

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.state = None
        self.action = None
        self.reward = None
        self.randomaction *= 0.95
        self.learningrate *= 0.99

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        
        # TODO: Update state
        currentstate = (inputs['light'],inputs['oncoming'],inputs['left'],inputs['right'],self.next_waypoint)
        
        # TODO: Select action according to your policy
        if self.randomaction > random.random():
        	action = random.choice(self.valid_action)
        	print 'Who care that fucking poliy, let pick by coins!'
        else:
        	action = np.argmax(self.Q[currentstate])

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        if self.state is not None:
        	estQ = self.reward + self.discount * max(self.Q.get_value(index=a,col=currentstate) for a in self.valid_action)
        	learnValue = (1-self.learningrate) * self.Q.get_value(index=self.action,col=self.state) + self.learningrate * estQ
        	self.Q.set_value(index=self.action,col=self.state,value=learnValue)
        	
        self.state = currentstate
        self.action = action
        self.reward = reward

        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]



def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.08, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
