import numpy as np

class Robot(object):
    def __init__(self, maze_dim):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        '''

        self.location = [0,0,0]
        self.maze_dim = maze_dim
        self.maze = [[-1 for c in range(maze_dim)] for r in range(maze_dim)] # record maze information
        
        self.goal = [[maze_dim/2,maze_dim/2],
                     [maze_dim/2-1,maze_dim/2],
                     [maze_dim/2,maze_dim/2-1],
                     [maze_dim/2-1,maze_dim/2-1]]
        self.heuristic = self.compute_heuristic(maze_dim)
        self.first_run = True
        self.stack = []
        self.count = 0   # record cost need in mapping maze
        self.policy = [] # record best move which can take agent to center ASAP, it is ambiguous
        

    def next_move(self, sensors):
        '''
        Use this function to determine the next move the robot should make,
        based on the input from the sensors after its previous move. Sensor
        inputs are a list of three distances from the robot's left, front, and
        right-facing sensors, in that order.

        Outputs should be a tuple of two values. The first value indicates
        robot rotation (if any), as a number: 0 for no rotation, +90 for a
        90-degree rotation clockwise, and -90 for a 90-degree rotation
        counterclockwise. Other values will result in no rotation. The second
        value indicates robot movement, and the robot will attempt to move the
        number of indicated squares: a positive number indicates forwards
        movement, while a negative number indicates backwards movement. The
        robot may move a maximum of three units per turn. Any excess movement
        is ignored.

        If the robot wants to end a run (e.g. during the first training run in
        the maze) then returing the tuple ('Reset', 'Reset') will indicate to
        the tester to end the run and return the robot to the start.
        '''
        if self.first_run:
        	""" mapping the whole maze """
        	self.count += 1
        	self.maze[self.location[0]][self.location[1]] = self.compute_maze_cell_num(sensors)
        	rotation,movement,self.location = self.explore_maze(sensors)
        	
        else:
        	move = self.policy.pop()
        	location = self.update_location(move[0],move[1],self.location)
        	print '------------------------'
        	print 'x=%s, y=%s, theta=%s'%(self.location[0],self.location[1],self.location[2])
        	print 'rotation:%s, movement:%s'%(move[0],move[1])
        	print 'x=%s, y=%s, theta=%s'%(location[0],location[1],location[2])
        	print '------------------------'
        	self.location = location
        	rotation,movement = move[0],move[1]

        return rotation, movement

    def compute_heuristic(self,maze_dim):
    	h = [[self.compute_L1_distance(x,y) for y in range(maze_dim)] for x in range(maze_dim)]
    	return h

    def compute_L1_distance(self,x,y):
    	return min(abs(x-goal[0])+abs(y-goal[1]) for goal in self.goal)
    	

    def explore_maze(self,sensors):
    	""" non-recursion version DFS """
    	if len(self.stack)>0 and self.stack[-1][0] != 0:
    		backward = self.stack.pop()
    		return backward[0],backward[1],backward[2]

    	possible_move = [move for move in self.compute_valid_move(sensors) if (move is not None) and (self.maze[move[-1][0]][move[-1][1]] == -1)]
    	#print sensors
    	#print possible_move
    	if len(possible_move) > 0:
    		move = possible_move.pop(0)
    		rotation,movement,location = move[0],move[1],move[2]

    		if rotation != 0:
    			backward = [-rotation,0,self.location]
    			self.stack.append(backward)
    		backward = [0,-movement,self.update_location(rotation,0,self.location)]
    		self.stack.append(backward)

    		return rotation,movement,location
    	else:
    		if len(self.stack)>0:
    			backward = self.stack.pop()
    			#print 'backward'
    			return backward[0],backward[1],backward[2]
    		else:
    			self.maze[0][0] = 1 # fix compute_maze_cell_num bug
    			for m in self.maze:
    				print m
    			print self.count
    			self.first_run = False
    			self.A_star() 
    			return 'Reset','Reset',[0,0,0]
    			


    def compute_valid_move(self,sensors):
    	if sensors[0] > 0:
       		yield [-90,1,self.update_location(-90,1,self.location)]
    	if sensors[1] > 0:
    		yield [0,1,self.update_location(0,1,self.location)]
    	if sensors[2] > 0:
    		yield [90,1,self.update_location(90,1,self.location)]



    def update_location(self,rotation,movement,location):
    	x,y,theta = location[0],location[1],location[2]
    	theta += rotation
    	theta %= 360
    	if theta == 0:
    		return [x+movement,y,theta]
    	elif theta == 90:
    		return [x,y+movement,theta]
    	elif theta == 180:
    		return [x-movement,y,theta]
    	elif theta == 270:
    		return [x,y-movement,theta]
    	else:
    		print 'invalid direction!!!'
    		raise RuntimeError

    def compute_maze_cell_num(self,sensors):
    	walls = {}
    	theta = self.location[-1]
    	r = -90
    	for s in sensors:
    		walls[(theta+r)%360] = 1 if s>0 else 0
    		r += 90
    	walls[(theta+180)%360] = 1
    	num = 0
    	for key,value in walls.items():
    		num += 2**(key/90) * value
    	return num



    def A_star(self):

    	open = []
    	resign = False
    	found = False

    	x,y,theta = 0,0,0
    	g,h = 0,self.heuristic[0][0]
    	f = g+h

    	valid_rotation = [-90,0,90]
    	valid_movement = [1,2,3] # -3,-2,-1,0 are useless

    	marked = [[False for c in range(self.maze_dim)] for r in range(self.maze_dim)]
    	path = {}

    	open.append([x,y,theta,g,f])

    	while not found and not resign:   
    		if len(open) == 0:
    			resign = True
    			print 'fail'
    			return 'fail'
    		else:
    			#print open
    			open.sort(key=lambda o:(o[-1],o[3]))
    			o = open.pop(0)

    			x,y,theta,g,f = o[0],o[1],o[2],o[3],o[4]
    			location = [x,y,theta]
    			try:
    				path[g].append([x,y,theta])
    			except KeyError:
    				path[g] = [[x,y,theta]]

    			if [x,y] in self.goal:
    				found = True
    			else:
    				sensors = self.sensor(x,y,theta)

    				for si in range(3):
    					for m in range(min(sensors[si],3),0,-1):
    						location2 = self.update_location(valid_rotation[si],m,location)
    						x2,y2,theta2 = location2[0],location2[1],location2[2]
    						if not marked[x2][y2]:
    							
    							g2 = g + 1
    							f2 = g2 + self.heuristic[x2][y2]
    							open.append([x2,y2,theta2,g2,f2])
    							marked[x][y] = True
    							

    	for i in range(g,-1,-1):    # compute path after A* found the best solution
    		if i == g:
    			x_last = path[i][0][0]
    			y_last = path[i][0][1]
    			theta_last = path[i][0][2]
    			
    		else:
    			store = {}
    			for p in path[i]:
    				x_temp,y_temp,theta_temp = p[0],p[1],p[2]
    				sensors = self.sensor(x_temp,y_temp,theta_temp)
    				for si in range(3):
    					for m in range(min(sensors[si],3),0,-1):
    						location_temp = self.update_location(valid_rotation[si],m,p)
    						if location_temp[0] == x_last and location_temp[1] == y_last and location_temp[2] == theta_last:
    							store[(valid_rotation[si],m)] = p

    			best_move = max(store,key=lambda k:k[1])
    			best_p = store[best_move]
    			self.policy.append(best_move)
    			x_last,y_last,theta_last = best_p[0],best_p[1],best_p[2]


    def sensor(self,x,y,theta):
    	sensors = [0,0,0]

    	r = -90

    	for i in range(3):
    		num = 15
    		if (theta + r) % 360 == 0:
    			for xx in range(x,self.maze_dim):
    				num &= self.maze[xx][y]
    				if num & 1 == 1:
    					sensors[i] += 1
    				else:
    					break

    		if (theta + r) % 360 == 90:
    			for yy in range(y,self.maze_dim):
    				num &=  self.maze[x][yy]
    				if num & 2 == 2:
    					sensors[i] += 1
    				else:
    					break

    		if (theta + r) % 360 == 180:
    			for xx in range(x,-1,-1):
    				num &= self.maze[xx][y]
    				if num & 4 == 4:
    					sensors[i] += 1
    				else:
    					break

    		if (theta + r) % 360 == 270:
    			for yy in range(y,-1,-1):
    				num &= self.maze[x][yy]
    				if num & 8 == 8:
    					sensors[i] += 1
    				else:
    					break

    		r += 90

    	return sensors

