import argparse
from numpy import random
from math import log
from engine import SimulationEngine
from event_type import EventType
from queue import Queue
from random import randint
import sys
import time

# Creating optional flag arguments for simulation
def check_arg(args=None):
    parser = argparse.ArgumentParser(description='Script to learn basic argparse')
    parser.add_argument('-d', '--debugmode',
                        help='Whether or not to print trace of simulation execution, if 1 trace is done, if 0, is not done',
                        default='0')
    parser.add_argument('-a', '--atlantic',
                        help='The mean arrival time of cars on Atlantic Dr, by default is set to 6',
                        default='6')
    parser.add_argument('-f', '--fourteenth',
                        help='The mean arrival time of cars on 14th Street, by default set to 0.1',
                        default='0.1')
    parser.add_argument('-g', '--greenlighttime',
                        help='Length of time 14th street light is green (and atlantic is red)',
                        default='45')
    parser.add_argument('-r', '--redlighttime',
                        help='Length of time 14th street light is red (and atlantic is green)',
                        default='30')
    parser.add_argument('-l', '--light',
                        help='Whether traffic light is used in simulation, by default is false',
                        default='False')
    parser.add_argument('-t', '--simtime',
                        help='Length of time the simulation runs, default is 500',
                        default='500')
    results = parser.parse_args(args)
    return (results.debugmode,
            results.atlantic,
            results.fourteenth,
            results.greenlighttime,
            results.redlighttime,
            results.light,
            results.simtime)

# Global variables
class GlobalVar: 
    # Constants used in simulation, not in python, these are functionlly
    # NOT constants, so be sure not to change these values
    # GoAcross = Time for car to go straight across any intersection
    # TurnRight = Time for car to turn right at any intersection
    # TurnLeft = Time for car to turn left at any intersection
    # GreenLightDuration = Time traffic light stays green for 14 st cars traveling west.
    # RedLightDuration = Time traffic light stays red for 14 St cars traveling west 
    #   (shorter since 14 St has a higher traffic volume than State St)
    GoAcross = 2.0
    TurnRight = 3.0
    TurnLeft = 4.0
    GreenLightDuration = 45
    RedLightDuration = 30

    # If traffic light is used in simulation, this will be true
    TrafficLight = False

    HighVolume14 = .1
    HighVolumeAtlantic = 6

    MediumVolume14 = 6
    MediumVolumeAtlantic = 9

    LowVolume14 = 10
    LowVolumeAtlantic = 15

    # Flag set to 1 to print debugging statements (event trace), 0 otherwise
    DB = 0

    # Used to determine length of simulation run, this is a time amount rather than 
    # number arrivals amount
    SimulationDuration = 500

    # Initialize simulation clock variable
    Now = 0.0

    # Number of events executed over course of simulation
    NumEvents = 0

    # State variables used for statistics
    TotalWaitingTime = 0.0  # Total time waiting to land
    LastEventTime = 0.0     # Time of last event processed; used to compute TotalWaitingTime

    # State variables of the simulation
    _14LightGreen = True                        # True if light is green for 14 street, false if red for 14 street
    _AtlanticLightGreen = not _14LightGreen     # Opposite boolean value of _14Stlight
    N_Atlantic_14_Free = True       # True if northern part of intersection is open to traverse
    S_Atlantic_14_Free = True       # True if southern part of intersection is open to traverse
    W_Atlantic_14_Free = True       # True is west part of intersection is open to traverse
    E_Atlantic_14_Free = True       # True if east part of intersection is open to traverse

    # N_14_E Attributes, Cars heading east in northern lane of 14st west of Atlantic Dr
    n14e_total_waiting_time = 0.0   # Total waiting time for n14e cars
    n14e_last_event_time = 0.0      # Time of last event processed for n14e event 
    n14e_queue = Queue()            # Queue to model cars lining up at stop light
    n14e_arrival_count = 0          # Number of cars that have entered this segment of road
    n14e_mean_arrival = HighVolume14         # Rate of arrival, lambda using exponential

    # S_14_E Attributes, Cars heading east in southern lane of 14st west of Atlantic Dr
    s14e_total_waiting_time = 0.0   # Total waiting time for s14e cars
    s14e_last_event_time = 0.0      # Time of last event processed for s14e event 
    s14e_queue = Queue()            # Queue to model cars lining up at stop light
    s14e_arrival_count = 0          # Number of cars that have entered this segment of road
    s14e_mean_arrival = HighVolume14         # Rate of arrival, lambda using exponential

    # EN_14_W Attributes, Cars heading west in northern lane of 14st east of Atlantic Dr
    en14w_total_waiting_time = 0.0  # Total waiting time for en14w cars
    en14w_last_event_time = 0.0     # Time of last event processed for en14w event 
    en14w_queue = Queue()           # Queue to model cars lining up at stop light
    en14w_arrival_count = 0         # Number of cars that have entered this segment of road
    en14w_mean_arrival = HighVolume14        # Rate of arrival, lambda using exponential

    # ES_14_W Attributes, Cars heading west in southern lane of 14st west of Atlantic Dr
    es14w_total_waiting_time = 0.0  # Total waiting time for es14w cars
    es14w_last_event_time = 0.0     # Time of last event processed for es14w event 
    es14w_queue = Queue()           # Queue to model cars lining up at stop light
    es14w_arrival_count = 0         # Number of cars that have entered this segment of road
    es14w_mean_arrival = HighVolume14        # Rate of arrival, lambda using exponential

    # N_Atlantic_S Attributes, Cars heading south on Atlantic Dr north of 14th St
    n_atlantic_s_total_waiting_time = 0.0   # Total waiting time for n_atlantic_s cars
    n_atlantic_s_last_event_time = 0.0      # Time of last event processed for n_atlantic_s event 
    n_atlantic_s_queue = Queue()            # Queue to model cars lining up at stop light
    n_atlantic_s_arrival_count = 0          # Number of cars that have entered this segment of road
    n_atlantic_s_mean_arrival = HighVolumeAtlantic         # Rate of arrival, lambda using exponential

    # S_Atlantic_N Attributes, Cars heading north on Atlantic Dr south of 14th St
    s_atlantic_n_total_waiting_time = 0.0   # Total waiting time for s_atlantic_n cars
    s_atlantic_n_last_event_time = 0.0      # Time of last event processed for s_atlantic_n event
    s_atlantic_n_queue = Queue()            # Queue to model cars lining up at stop light
    s_atlantic_n_arrival_count = 0          # Number of cars that have entered this segment of road
    s_atlantic_n_mean_arrival = HighVolumeAtlantic       # Rate of arrival, lambda using exponential

# Assigning global vales the values passed in with flags, or default values if no values passed in
if __name__ == '__main__':
    print 'Welcome to the 14St, Atlantic Dr Intersection Simulation'
    print '\nHere are the simulation parameters:'
    debugmode, atlantic, fourteenth, greenlighttime, redlighttime, light, simtime = check_arg(sys.argv[1:])
    GlobalVar.DB = int(debugmode)
    if light == "True" or light == "T" or light == "true" or light == "t":
        GlobalVar.TrafficLight = True
        print '  Traffic light used:', GlobalVar.TrafficLight
        print '  Green light time:', int(greenlighttime)
        print '  Red light time:', int(redlighttime)
    else:
        print '  Traffic light used:', GlobalVar.TrafficLight
    GlobalVar.SimulationDuration = int(simtime)
    GlobalVar.GreenLightDuration = int(greenlighttime)
    GlobalVar.RedLightDuration = int(redlighttime)
    print '  Debug mode:', int(debugmode)
    print '  Simulation duration:', simtime
    # Update all the mean arrival times for atlantic drive
    atlantic_arrival_rate = float(atlantic)
    GlobalVar.n_atlantic_s_mean_arrival = atlantic_arrival_rate       # Rate of arrival, lambda using exponential
    GlobalVar.s_atlantic_n_mean_arrival = atlantic_arrival_rate       # Rate of arrival, lambda using exponential
    print '  N Atlantic S Mean Arrival:', GlobalVar.n_atlantic_s_mean_arrival
    print '  S Atlantic N Mean Arrival:', GlobalVar.s_atlantic_n_mean_arrival

    # Update all the mean arrival times for fourteenth street
    fourteenth_arrival_rate = float(fourteenth)
    GlobalVar.n14e_mean_arrival = fourteenth_arrival_rate         # Rate of arrival, lambda using exponential
    GlobalVar.s14e_mean_arrival = fourteenth_arrival_rate         # Rate of arrival, lambda using exponential
    GlobalVar.en14w_mean_arrival = fourteenth_arrival_rate        # Rate of arrival, lambda using exponential
    GlobalVar.es14w_mean_arrival = fourteenth_arrival_rate        # Rate of arrival, lambda using exponential
    print '  N 14 E Mean Arrival:', GlobalVar.n14e_mean_arrival
    print '  S 14 E Mean Arrival:', GlobalVar.s14e_mean_arrival
    print '  EN 14 W Mean Arrival:', GlobalVar.en14w_mean_arrival
    print '  ES 14 W Mean Arrival:', GlobalVar.es14w_mean_arrival

# Initialize simulation engine, which is a future event list, which is a linked list
# Note this needs to be accessible from various functions, so am making this a global object
# Interestingly, it does not seem necessary to use global keyword before it
simulation_engine = SimulationEngine()

###### Random Number Generator
# Compute exponenitally distributed random number with mean provided. The expected value is
# the mean provided, but because from probability distribution, there will be variance from expected value
def rand_exp(mean):
    uniform_random = random.uniform(0, 1)
    return (-mean * log(1.0 - uniform_random))

# Generates a uniformally distributed random number [0, 1)
def random_uniform():
    return random.uniform(0, 1)

# Assumption is that most cars will go straight across the intersection
def get_turn_direction():
    random_variable = random_uniform()
    if random_variable < 0.5:
        return "straight"
    elif random_variable >= 0.5 and random_variable < 0.75:
        return "left"
    else:
        return "right"

# Those roads with more traffic are weighted higher to increase chance of arrival
# This determines the volume of traffic
def determine_next_arrival():
    random_int = randint(1, 225)
    if random_int in range(1,50):
        # print 'n14e arrival scheduled'
        return {'mean': GlobalVar.n14e_mean_arrival, 'event_type': EventType.N14E_ARRIVAL, 'callback': n14e_arrival}
    if random_int in range(50,100):
        # print 's14e arrival scheduled'
        return {'mean': GlobalVar.s14e_mean_arrival, 'event_type': EventType.S14E_ARRIVAL, 'callback': s14e_arrival}
    if random_int in range(100,150):
        # print 'en14w arrival scheduled'
        return {'mean': GlobalVar.en14w_mean_arrival, 'event_type': EventType.EN14W_ARRIVAL, 'callback': en14w_arrival} 
    if random_int in range(150,200):
        # print 'es14w arrival scheduled'
        return {'mean': GlobalVar.es14w_mean_arrival, 'event_type': EventType.ES14W_ARRIVAL, 'callback': es14w_arrival}
    if random_int in range(200,213):
        # print 'n_atlantic_s arrival scheduled'
        return {'mean': GlobalVar.n_atlantic_s_mean_arrival, 'event_type': EventType.N_ATLANTIC_S_ARRIVAL, 'callback': n_atlantic_s_arrival}
    if random_int in range(213,226):
        # print 's_atlantic_n arrival scheduled'
        return {'mean': GlobalVar.s_atlantic_n_mean_arrival, 'event_type': EventType.S_ATLANTIC_N_ARRIVAL, 'callback': s_atlantic_n_arrival} 

# Same function as above but with traffic light
def determine_next_arrival_traffic_light():
    random_int = randint(1, 225)
    if random_int in range(1,50):
        # print 'n14e arrival scheduled'
        return {'mean': GlobalVar.n14e_mean_arrival, 'event_type': EventType.N14E_ARRIVAL_TL, 'callback': n14e_arrival_traffic_light}
    if random_int in range(50,100):
        # print 's14e arrival scheduled'
        return {'mean': GlobalVar.s14e_mean_arrival, 'event_type': EventType.S14E_ARRIVAL_TL, 'callback': s14e_arrival_traffic_light}
    if random_int in range(100,150):
        # print 'en14w arrival scheduled'
        return {'mean': GlobalVar.en14w_mean_arrival, 'event_type': EventType.EN14W_ARRIVAL_TL, 'callback': en14w_arrival_traffic_light} 
    if random_int in range(150,200):
        # print 'es14w arrival scheduled'
        return {'mean': GlobalVar.es14w_mean_arrival, 'event_type': EventType.ES14W_ARRIVAL_TL, 'callback': es14w_arrival_traffic_light}
    if random_int in range(200,213):
        # print 'n_atlantic_s arrival scheduled'
        return {'mean': GlobalVar.n_atlantic_s_mean_arrival, 'event_type': EventType.N_ATLANTIC_S_ARRIVAL_TL, 'callback': n_atlantic_s_arrival_traffic_light}
    if random_int in range(213,226):
        # print 's_atlantic_n arrival scheduled'
        return {'mean': GlobalVar.s_atlantic_n_mean_arrival, 'event_type': EventType.S_ATLANTIC_N_ARRIVAL_TL, 'callback': s_atlantic_n_arrival_traffic_light} 

###### Simulation time keeper
def current_time():
    return GlobalVar.Now

# While this light is green, cars can continue to arrive on any street and pass through if on 14 street
def _14_light_turns_green(event_data):
    # If something bad happens
    if event_data != EventType._14_LIGHT_TURNS_GREEN:
        print "In _14_light_turns_green, unexpected event type %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "Light turns green, time = %f" % current_time()

    GlobalVar._14LightGreen = True
    GlobalVar._AtlanticLightGreen = not GlobalVar._14LightGreen

    # Schedule another arrival if there is still time
    # It is using a value from an exponential distribution to determine exactly when the
    # next plane is to arrive
    # Need to schedule event to change traffic light to red
    time = current_time()
    if time < GlobalVar.SimulationDuration:
        new_event_type = EventType._14_LIGHT_TURNS_RED
        timestamp = current_time() + GlobalVar.GreenLightDuration
        simulation_engine.schedule_new_event(timestamp, new_event_type, _14_light_turns_red)

    # Need to check on traffic in both directions
    if not GlobalVar.es14w_queue.isEmpty():
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.ES14W_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, es14w_go_across_traffic_light)
    
    if not GlobalVar.en14w_queue.isEmpty():
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.EN14W_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, en14w_go_across_traffic_light)

    if not GlobalVar.n14e_queue.isEmpty():
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.N14E_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, n14e_go_across_traffic_light)
    
    if not GlobalVar.s14e_queue.isEmpty():
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.S14E_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, s14e_go_across_traffic_light)

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

# While this light is green, cars can continue to arrive on any street and pass through if on 14 street
def _14_light_turns_red(event_data):
    # If something bad happens
    if event_data != EventType._14_LIGHT_TURNS_RED:
        print "In _14_light_turns_red, unexpected event type %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "Light turns red, time = %f" % current_time()

    GlobalVar._14LightGreen = False
    GlobalVar._AtlanticLightGreen = not GlobalVar._14LightGreen

    # Schedule another arrival if there is still time
    # It is using a value from an exponential distribution to determine exactly when the
    # next plane is to arrive
    # Need to schedule event to change traffic light to green
    time = current_time()
    if time < GlobalVar.SimulationDuration:
        new_event_type = EventType._14_LIGHT_TURNS_GREEN
        timestamp = current_time() + GlobalVar.RedLightDuration
        simulation_engine.schedule_new_event(timestamp, new_event_type, _14_light_turns_green)

        # Need to check on traffic in both directions
    if not GlobalVar.n_atlantic_s_queue.isEmpty():
        GlobalVar.W_Atlantic_14_Free = False
        new_event_type = EventType.N_ATLANTIC_S_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_go_across_traffic_light)
    
    if not GlobalVar.s_atlantic_n_queue.isEmpty():
        GlobalVar.E_Atlantic_14_Free = False
        new_event_type = EventType.S_ATLANTIC_N_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_go_across_traffic_light)

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

# Event handler for a car arriving at northern lane of 14th street from the west, west of atlantic
def n14e_arrival(event_data):
    # If something bad happens
    if event_data != EventType.N14E_ARRIVAL:
        print "Unexpected event type in n14e_arrival, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "N14E_ARRIVAL Event, time: %f" % current_time()
    
    # Get identity of car
    car_identity = 'n14e_car_%d' % (GlobalVar.n14e_arrival_count + 1)

    # Add newly arrived car to queue to simulate arriving at intersection
    GlobalVar.n14e_queue.enqueue(car_identity)
    
    # Update waiting time statistics
    if GlobalVar.n14e_queue.size() > 1:
        GlobalVar.n14e_total_waiting_time += \
            ( (GlobalVar.n14e_queue.size() - 1) * (current_time() - GlobalVar.n14e_last_event_time))

    # Update Statistics
    GlobalVar.NumEvents += 1
    GlobalVar.n14e_arrival_count += 1

    # Schedule another arrival if there is still time
    # It is using a value from an exponential distribution to determine exactly when the
    # next plane is to arrive
    time = current_time()
    if time < GlobalVar.SimulationDuration:
        next_arrival = determine_next_arrival()
        # If in debug mode
        if GlobalVar.DB:
            print 'Next arrival is: ',
            print next_arrival
        new_event_type = next_arrival['event_type']
        timestamp = current_time() + rand_exp(next_arrival['mean'])
        callback = next_arrival['callback']
        simulation_engine.schedule_new_event(timestamp, new_event_type, callback)

    # Determine which direction to go, Right, Straight, or Left
    turn_direction = get_turn_direction()
    if turn_direction is "straight" or turn_direction is "right":
        # Event for N_14_E Go Across
        # Southern part of intersection no longer free for cars to turn across
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.N14E_GO_ACROSS
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, n14e_go_across)
    # Can make a left turn if no car is traversing northern part of intersection
    elif turn_direction is "left" and GlobalVar.N_Atlantic_14_Free:
        # Event for N_14_E Turn Left
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.N14E_TURN_LEFT
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, n14e_turn_left)

    # Time of last event processed
    GlobalVar.n14e_last_event_time = current_time()

# Event handler for cars turning left from northern lane of 14st east across to Atlnatic Dr north
def n14e_turn_left(event_data):
    # If something bad happens
    if event_data != EventType.N14E_TURN_LEFT:
        print "Unexpected event type in n14e_turn_left, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "N14E Turn Left event, time: %f" % current_time()
    if GlobalVar.n14e_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''
    
    # Remove car from n14e queue
    car_removed = GlobalVar.n14e_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across N14E" % car_removed
        print "%d cars now in n14e_queue" % GlobalVar.n14e_queue.size()
        print "n14e_queue.isEmpty() is: ",
        print GlobalVar.n14e_queue.isEmpty()
    
    # Update waiting time statistics
    if GlobalVar.n14e_queue.size() > 1:
        GlobalVar.n14e_total_waiting_time += \
        ( (GlobalVar.n14e_queue.size() - 1) * (current_time() - GlobalVar.n14e_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern part of intersection is now free for cars to turn across
    GlobalVar.N_Atlantic_14_Free = True

    # Time of last event processed
    GlobalVar.n14e_last_event_time = current_time()

# Event handler for cars going across atlantic dr intersection on n14e
def n14e_go_across(event_data):
    # If something bad happens
    if event_data != EventType.N14E_GO_ACROSS:
        print "Unexpected event type in n14e_go_across, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "N14E Go Across event, time: %f" % current_time()
    if GlobalVar.n14e_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from n14e queue
    car_removed = GlobalVar.n14e_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across N14E" % car_removed
        print "%d cars now in n14e_queue" % GlobalVar.n14e_queue.size()
        print "n14e_queue.isEmpty() is: ",
        print GlobalVar.n14e_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.n14e_queue.size() > 1:
        GlobalVar.n14e_total_waiting_time += \
        ( (GlobalVar.n14e_queue.size() - 1) * (current_time() - GlobalVar.n14e_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Southern part of intersection is now free for cars to turn across
    GlobalVar.S_Atlantic_14_Free = True

    # Need to check if any other cars are waiting to cross this section of road
    # These sections are: es14w_turn_left, n_atlantic_s anything
    if not GlobalVar.es14w_queue.isEmpty():
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.ES14W_TURN_LEFT
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, es14w_turn_left)
    else:
        # flip a coin to determine which side of atlantic dr to let go
        coin = random_uniform()
        # print 'coin flip is %f' % coin
        if coin < 0.5:
            # Check n_atlantic_s
            if not GlobalVar.n_atlantic_s_queue.isEmpty():
                turn_direction = get_turn_direction()
                if turn_direction is "straight" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for N_ATLANTIC_S Go Across
                    # Northern and southern parts of intersection no longer free for cars to turn across
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.N_ATLANTIC_S_GO_ACROSS
                    timestamp = current_time() + GlobalVar.GoAcross
                    simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_go_across)
                # Can make a left turn if no car is traversing northern part of intersection
                elif turn_direction is "left" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for N_ATLANTIC_S Turn Left
                    # This is now blocking the southern part of atlantic intersection
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.N_ATLANTIC_S_TURN_LEFT
                    timestamp = current_time() + GlobalVar.TurnLeft
                    simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_left)
                elif turn_direction is "right" and GlobalVar.N_Atlantic_14_Free:
                    GlobalVar.N_Atlantic_14_Free = False
                    new_event_type = EventType.N_ATLANTIC_S_TURN_RIGHT
                    timestamp = current_time() + GlobalVar.TurnRight
                    simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_right)
        else:
            # Check s_atlantic_n
            if not GlobalVar.s_atlantic_n_queue.isEmpty():
                turn_direction = get_turn_direction()
                if turn_direction is "straight" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for S_ATLANTIC_N Go Across
                    # Northern and southern parts of intersection no longer free for cars to turn across
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.S_ATLANTIC_N_GO_ACROSS
                    timestamp = current_time() + GlobalVar.GoAcross
                    simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_go_across)
                # Can make a left turn if no car is traversing northern part of intersection
                elif turn_direction is "left" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for S_ATLANTIC_N Turn Left
                    # This is now blocking the southern part of atlantic intersection
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.S_ATLANTIC_N_TURN_LEFT
                    timestamp = current_time() + GlobalVar.TurnLeft
                    simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_left)
                elif turn_direction is "right" and GlobalVar.N_Atlantic_14_Free:
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.S_ATLANTIC_N_TURN_RIGHT
                    timestamp = current_time() + GlobalVar.TurnRight
                    simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_right)

    # Time of last event processed
    GlobalVar.n14e_last_event_time = current_time()

# Event handler for a car arriving at southern lane of 14th street from the west, west of atlantic
def s14e_arrival(event_data):
    # If something bad happens
    if event_data != EventType.S14E_ARRIVAL:
        print "Unexpected event type in s14e_arrival, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "S14E_ARRIVAL Event: time=%f" % current_time()
    
    # Get identity of car
    car_identity = 's14e_car_%d' % (GlobalVar.s14e_arrival_count + 1)

    # Add newly arrived car to queue to simulate arriving at intersection
    GlobalVar.s14e_queue.enqueue(car_identity)
    
    # Update waiting time statistics
    if GlobalVar.s14e_queue.size() > 1:
        GlobalVar.s14e_total_waiting_time += \
            ( (GlobalVar.s14e_queue.size() - 1) * (current_time() - GlobalVar.s14e_last_event_time))

    # Update Statistics
    GlobalVar.NumEvents += 1
    GlobalVar.s14e_arrival_count += 1

    # Schedule another arrival if there is still time
    # It is using a value from an exponential distribution to determine exactly when the
    # next plane is to arrive
    time = current_time()
    if time < GlobalVar.SimulationDuration:
        next_arrival = determine_next_arrival()
        # If in debug mode
        if GlobalVar.DB:
            print 'Next arrival is: ',
            print next_arrival
        new_event_type = next_arrival['event_type']
        timestamp = current_time() + rand_exp(next_arrival['mean'])
        callback = next_arrival['callback']
        simulation_engine.schedule_new_event(timestamp, new_event_type, callback)

    # Determine which direction to go, Right, Straight, or Left
    turn_direction = get_turn_direction()
    if turn_direction is "straight" or turn_direction is "left":
        # Event for s14e Go Across
        # Southern part of intersection no longer free for cars to turn across
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.S14E_GO_ACROSS
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, s14e_go_across)
    # Can make a left turn if no car is traversing northern part of intersection
    elif turn_direction is "right":
        # Event for S_14_E Turn Right
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.S14E_TURN_RIGHT
        timestamp = current_time() + GlobalVar.TurnRight
        simulation_engine.schedule_new_event(timestamp, new_event_type, s14e_turn_right)

    # Time of last event processed
    GlobalVar.s14e_last_event_time = current_time()

# Event handler for cars going across atlantic dr intersection on s14e
def s14e_go_across(event_data):
    # If something bad happens
    if event_data != EventType.S14E_GO_ACROSS:
        print "Unexpected event type in s14e_go_across, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "S14E Go Across event, time: %f" % current_time()
    if GlobalVar.s14e_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from s14e queue
    car_removed = GlobalVar.s14e_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across S14E" % car_removed
        print "%d cars now in s14e_queue" % GlobalVar.s14e_queue.size()
        print "s14e_queue.isEmpty() is: ",
        print GlobalVar.s14e_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.s14e_queue.size() > 1:
        GlobalVar.s14e_total_waiting_time += \
        ( (GlobalVar.s14e_queue.size() - 1) * (current_time() - GlobalVar.s14e_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Southern part of intersection is now free for cars to turn across
    GlobalVar.S_Atlantic_14_Free = True

    # Need to check if any other cars are waiting to cross this section of road
    # These sections are: es14w_turn_left
    if not GlobalVar.es14w_queue.isEmpty():
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.ES14W_TURN_LEFT
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, es14w_turn_left)
    else:
        # flip a coin to determine which side of atlantic dr to let go
        coin = random_uniform()
        # print 'coin flip is %f' % coin
        if coin < 0.5:
            # Check n_atlantic_s
            if not GlobalVar.n_atlantic_s_queue.isEmpty():
                turn_direction = get_turn_direction()
                if turn_direction is "straight" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for N_ATLANTIC_S Go Across
                    # Northern and southern parts of intersection no longer free for cars to turn across
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.N_ATLANTIC_S_GO_ACROSS
                    timestamp = current_time() + GlobalVar.GoAcross
                    simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_go_across)
                # Can make a left turn if no car is traversing northern part of intersection
                elif turn_direction is "left" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for N_ATLANTIC_S Turn Left
                    # This is now blocking the southern part of atlantic intersection
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.N_ATLANTIC_S_TURN_LEFT
                    timestamp = current_time() + GlobalVar.TurnLeft
                    simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_left)
                elif turn_direction is "right" and GlobalVar.N_Atlantic_14_Free:
                    GlobalVar.N_Atlantic_14_Free = False
                    new_event_type = EventType.N_ATLANTIC_S_TURN_RIGHT
                    timestamp = current_time() + GlobalVar.TurnRight
                    simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_right)
        else:
            # Check s_atlantic_n
            if not GlobalVar.s_atlantic_n_queue.isEmpty():
                turn_direction = get_turn_direction()
                if turn_direction is "straight" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for S_ATLANTIC_N Go Across
                    # Northern and southern parts of intersection no longer free for cars to turn across
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.S_ATLANTIC_N_GO_ACROSS
                    timestamp = current_time() + GlobalVar.GoAcross
                    simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_go_across)
                # Can make a left turn if no car is traversing northern part of intersection
                elif turn_direction is "left" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for S_ATLANTIC_N Turn Left
                    # This is now blocking the southern part of atlantic intersection
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.S_ATLANTIC_N_TURN_LEFT
                    timestamp = current_time() + GlobalVar.TurnLeft
                    simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_left)
                elif turn_direction is "right" and GlobalVar.N_Atlantic_14_Free:
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.S_ATLANTIC_N_TURN_RIGHT
                    timestamp = current_time() + GlobalVar.TurnRight
                    simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_right)

    # Time of last event processed
    GlobalVar.s14e_last_event_time = current_time()

# Event handler for cars turning right onto atlantic dr from s14e
def s14e_turn_right(event_data):
    # If something bad happens
    if event_data != EventType.S14E_TURN_RIGHT:
        print "Unexpected event type in s14e_turn_right, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "S14E Turn Right event, time: %f" % current_time()
    if GlobalVar.s14e_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from s14e queue
    car_removed = GlobalVar.s14e_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went right from S14E onto Atlantic Dr south" % car_removed
        print "%d cars now in s14e_queue" % GlobalVar.s14e_queue.size()
        print "s14e_queue.isEmpty() is: ",
        print GlobalVar.s14e_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.s14e_queue.size() > 1:
        GlobalVar.s14e_total_waiting_time += \
        ( (GlobalVar.s14e_queue.size() - 1) * (current_time() - GlobalVar.s14e_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Update southern part of Atlantic_14 intersection to be free
    GlobalVar.S_Atlantic_14_Free = True

    # Time of last event processed
    GlobalVar.s14e_last_event_time = current_time()

# Event handler for a car arriving at northern lane of 14th street from the east, east of atlantic 
def en14w_arrival(event_data):
 # If something bad happens
    if event_data != EventType.EN14W_ARRIVAL:
        print "Unexpected event type in es14w_arrival, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "EN14W_ARRIVAL Event, time = %f" % current_time()
    
    # Get identity of car
    car_identity = 'en14w_car_%d' % (GlobalVar.en14w_arrival_count + 1)

    # Add newly arrived car to queue to simulate arriving at intersection
    GlobalVar.en14w_queue.enqueue(car_identity)
    
    # Update waiting time statistics
    if GlobalVar.en14w_queue.size() > 1:
        if GlobalVar.DB:
            print "en14w queue size greater than 1, is: %d" % GlobalVar.en14w_queue.size()
        GlobalVar.en14w_total_waiting_time += \
            ( (GlobalVar.en14w_queue.size() - 1) * (current_time() - GlobalVar.en14w_last_event_time))

    # Update Statistics
    GlobalVar.NumEvents += 1
    GlobalVar.en14w_arrival_count += 1

    # Schedule another arrival if there is still time
    # It is using a value from an exponential distribution to determine exactly when the
    # next plane is to arrive
    time = current_time()
    if time < GlobalVar.SimulationDuration:
        next_arrival = determine_next_arrival()
        # If in debug mode
        if GlobalVar.DB:
            print 'Next arrival is: ',
            print next_arrival
        new_event_type = next_arrival['event_type']
        timestamp = current_time() + rand_exp(next_arrival['mean'])
        callback = next_arrival['callback']
        simulation_engine.schedule_new_event(timestamp, new_event_type, callback)

    # Determine which direction to go, Right, Straight, or Left
    turn_direction = get_turn_direction()
    if turn_direction is "straight" or turn_direction is "left":
        # Event for EN14W Go Across
        # Northern part of intersection no longer free for cars to turn across
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.EN14W_GO_ACROSS
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, en14w_go_across)
    # Can make a left turn if no car is traversing northern part of intersection
    elif turn_direction is "right":
        # Event for EN14W Turn Right
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.EN14W_TURN_RIGHT
        timestamp = current_time() + GlobalVar.TurnRight
        simulation_engine.schedule_new_event(timestamp, new_event_type, en14w_turn_right)

    # Time of last event processed
    GlobalVar.en14w_last_event_time = current_time()

# Event handler for cars going across Atlantic Dr on EN14W
def en14w_go_across(event_data):
    # If something bad happens
    if event_data != EventType.EN14W_GO_ACROSS:
        print "Unexpected event type in es14w_go_across, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "EN14W Go Across event, time: %f" % current_time()
    if GlobalVar.en14w_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from en14w queue
    car_removed = GlobalVar.en14w_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across EN14W" % car_removed
        print "%d cars now in en14w_queue" % GlobalVar.en14w_queue.size()
        print "en14w_queue.isEmpty() is: ",
        print GlobalVar.en14w_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.en14w_queue.size() > 1:
        GlobalVar.en14w_total_waiting_time += \
        ( (GlobalVar.en14w_queue.size() - 1) * (current_time() - GlobalVar.en14w_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern part of intersection is now free for cars to turn across
    GlobalVar.N_Atlantic_14_Free = True

    # Need to check if any other cars are waiting to cross this section of road
    # These sections are: n14e_turn_left
    if not GlobalVar.n14e_queue.isEmpty():
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.N14E_TURN_LEFT
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, n14e_turn_left)
    else:
        # flip a coin to determine which side of atlantic dr to let go
        coin = random_uniform()
        # print 'coin flip is %f' % coin
        if coin < 0.5:
            # Check n_atlantic_s
            if not GlobalVar.n_atlantic_s_queue.isEmpty():
                turn_direction = get_turn_direction()
                if turn_direction is "straight" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for N_ATLANTIC_S Go Across
                    # Northern and southern parts of intersection no longer free for cars to turn across
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.N_ATLANTIC_S_GO_ACROSS
                    timestamp = current_time() + GlobalVar.GoAcross
                    simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_go_across)
                # Can make a left turn if no car is traversing northern part of intersection
                elif turn_direction is "left" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for N_ATLANTIC_S Turn Left
                    # This is now blocking the southern part of atlantic intersection
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.N_ATLANTIC_S_TURN_LEFT
                    timestamp = current_time() + GlobalVar.TurnLeft
                    simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_left)
                elif turn_direction is "right" and GlobalVar.N_Atlantic_14_Free:
                    GlobalVar.N_Atlantic_14_Free = False
                    new_event_type = EventType.N_ATLANTIC_S_TURN_RIGHT
                    timestamp = current_time() + GlobalVar.TurnRight
                    simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_right)
        else:
            # Check s_atlantic_n
            if not GlobalVar.s_atlantic_n_queue.isEmpty():
                turn_direction = get_turn_direction()
                if turn_direction is "straight" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for S_ATLANTIC_N Go Across
                    # Northern and southern parts of intersection no longer free for cars to turn across
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.S_ATLANTIC_N_GO_ACROSS
                    timestamp = current_time() + GlobalVar.GoAcross
                    simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_go_across)
                # Can make a left turn if no car is traversing northern part of intersection
                elif turn_direction is "left" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for S_ATLANTIC_N Turn Left
                    # This is now blocking the southern part of atlantic intersection
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.S_ATLANTIC_N_TURN_LEFT
                    timestamp = current_time() + GlobalVar.TurnLeft
                    simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_left)
                elif turn_direction is "right" and GlobalVar.N_Atlantic_14_Free:
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.S_ATLANTIC_N_TURN_RIGHT
                    timestamp = current_time() + GlobalVar.TurnRight
                    simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_right)

    # Time of last event processed
    GlobalVar.en14w_last_event_time = current_time()

# Event handler for cars turning right onto atlantic dr from en14w
def en14w_turn_right(event_data):
    # If something bad happens
    if event_data != EventType.EN14W_TURN_RIGHT:
        print "Unexpected event type in es14w_turn_right, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "EN14W Turn Right event, time: %f" % current_time()
    if GlobalVar.en14w_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from en14w queue
    car_removed = GlobalVar.en14w_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went right from EN14W onto Atlantic Dr south" % car_removed
        print "%d cars now in en14w_queue" % GlobalVar.en14w_queue.size()
        print "en14w_queue.isEmpty() is: ",
        print GlobalVar.en14w_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.en14w_queue.size() > 1:
        GlobalVar.en14w_total_waiting_time += \
        ( (GlobalVar.en14w_queue.size() - 1) * (current_time() - GlobalVar.en14w_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern part of intersection is now free for cars to turn across
    GlobalVar.N_Atlantic_14_Free = True

    # Time of last event processed
    GlobalVar.en14w_last_event_time = current_time()

# Event handler for a car arriving at southern lane of 14th street from the east, east of atlantic
def es14w_arrival(event_data):
 # If something bad happens
    if event_data != EventType.ES14W_ARRIVAL:
        print "Unexpected event type in es14w_arrival, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "ES14W_ARRIVAL Event, time = %f" % current_time()
    
    # Get identity of car
    car_identity = 'es14w_car_%d' % (GlobalVar.es14w_arrival_count + 1)

    # Add newly arrived car to queue to simulate arriving at intersection
    GlobalVar.es14w_queue.enqueue(car_identity)
    
    # Update waiting time statistics
    if GlobalVar.es14w_queue.size() > 1:
        GlobalVar.es14w_total_waiting_time += \
            ( (GlobalVar.es14w_queue.size() - 1) * (current_time() - GlobalVar.es14w_last_event_time))

    # Update Statistics
    GlobalVar.NumEvents += 1
    GlobalVar.es14w_arrival_count += 1

    # Schedule another arrival if there is still time
    # It is using a value from an exponential distribution to determine exactly when the
    # next plane is to arrive
    time = current_time()
    if time < GlobalVar.SimulationDuration:
        next_arrival = determine_next_arrival()
        # If in debug mode
        if GlobalVar.DB:
            print 'Next arrival is: ',
            print next_arrival
        new_event_type = next_arrival['event_type']
        timestamp = current_time() + rand_exp(next_arrival['mean'])
        callback = next_arrival['callback']
        simulation_engine.schedule_new_event(timestamp, new_event_type, callback)

    # Determine which direction to go, Right, Straight, or Left
    turn_direction = get_turn_direction()
    if turn_direction is "straight" or turn_direction is "right":
        # Event for ES14W Go Across
        # Northern part of intersection no longer free for cars to turn across
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.ES14W_GO_ACROSS
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, es14w_go_across)
    # Can make a left turn if no car is traversing southern part of intersection
    elif turn_direction is "left" and GlobalVar.S_Atlantic_14_Free:
        # Event for ES14W Turn Left
        # This is now blocking the southern part of atlantic intersection
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.ES14W_TURN_LEFT
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, es14w_turn_left)

    # Time of last event processed
    GlobalVar.es14w_last_event_time = current_time()

# Event handler for cars going across Atlantic Dr on ES14W
def es14w_go_across(event_data):
    # If something bad happens
    if event_data != EventType.ES14W_GO_ACROSS:
        print "Unexpected event type in es14w_go_across, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "ES14W Go Across event, time: %f" % current_time()
    if GlobalVar.es14w_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from es14w queue
    car_removed = GlobalVar.es14w_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across ES14W" % car_removed
        print "%d cars now in es14w_queue" % GlobalVar.es14w_queue.size()
        print "es14w_queue.isEmpty() is: ",
        print GlobalVar.es14w_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.es14w_queue.size() > 1:
        GlobalVar.es14w_total_waiting_time += \
        ( (GlobalVar.es14w_queue.size() - 1) * (current_time() - GlobalVar.es14w_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern part of intersection is now free for cars to turn across
    GlobalVar.N_Atlantic_14_Free = True

    # Need to check if any other cars are waiting to cross this section of road
    # These sections are: n14e_turn_left
    if not GlobalVar.n14e_queue.isEmpty():
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.N14E_TURN_LEFT
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, n14e_turn_left)
    else:
        # Need to put this into a separate method
        # flip a coin to determine which side of atlantic dr to let go
        coin = random_uniform()
        # print 'coin flip is %f' % coin
        if coin < 0.5:
            # Check n_atlantic_s
            if not GlobalVar.n_atlantic_s_queue.isEmpty():
                turn_direction = get_turn_direction()
                if turn_direction is "straight" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for N_ATLANTIC_S Go Across
                    # Northern and southern parts of intersection no longer free for cars to turn across
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.N_ATLANTIC_S_GO_ACROSS
                    timestamp = current_time() + GlobalVar.GoAcross
                    simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_go_across)
                # Can make a left turn if no car is traversing northern part of intersection
                elif turn_direction is "left" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for N_ATLANTIC_S Turn Left
                    # This is now blocking the southern part of atlantic intersection
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.N_ATLANTIC_S_TURN_LEFT
                    timestamp = current_time() + GlobalVar.TurnLeft
                    simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_left)
                elif turn_direction is "right" and GlobalVar.N_Atlantic_14_Free:
                    GlobalVar.N_Atlantic_14_Free = False
                    new_event_type = EventType.N_ATLANTIC_S_TURN_RIGHT
                    timestamp = current_time() + GlobalVar.TurnRight
                    simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_right)
        else:
            # Check s_atlantic_n
            if not GlobalVar.s_atlantic_n_queue.isEmpty():
                turn_direction = get_turn_direction()
                if turn_direction is "straight" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for S_ATLANTIC_N Go Across
                    # Northern and southern parts of intersection no longer free for cars to turn across
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.S_ATLANTIC_N_GO_ACROSS
                    timestamp = current_time() + GlobalVar.GoAcross
                    simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_go_across)
                # Can make a left turn if no car is traversing northern part of intersection
                elif turn_direction is "left" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
                    # Event for S_ATLANTIC_N Turn Left
                    # This is now blocking the southern part of atlantic intersection
                    GlobalVar.N_Atlantic_14_Free = False
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.S_ATLANTIC_N_TURN_LEFT
                    timestamp = current_time() + GlobalVar.TurnLeft
                    simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_left)
                elif turn_direction is "right" and GlobalVar.N_Atlantic_14_Free:
                    GlobalVar.S_Atlantic_14_Free = False
                    new_event_type = EventType.S_ATLANTIC_N_TURN_RIGHT
                    timestamp = current_time() + GlobalVar.TurnRight
                    simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_right)

    # Time of last event processed
    GlobalVar.es14w_last_event_time = current_time()

# Event handler for cars turning left from southern lane of 14st east across to Atlnatic Dr south
def es14w_turn_left(event_data):
    # If something bad happens
    if event_data != EventType.ES14W_TURN_LEFT:
        print "Unexpected event type in es14w_turn_left, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "ES14W Turn Left event, time: %f" % current_time()
    if GlobalVar.es14w_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''
    
    # Remove car from es14w queue
    car_removed = GlobalVar.es14w_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across ES14W" % car_removed
        print "%d cars now in es14w_queue" % GlobalVar.es14w_queue.size()
        print "es14w_queue.isEmpty() is: ",
        print GlobalVar.es14w_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.es14w_queue.size() > 1:
        GlobalVar.es14w_total_waiting_time += \
        ((GlobalVar.es14w_queue.size() - 1) * (current_time() - GlobalVar.es14w_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern part of intersection is now free for cars to turn across
    GlobalVar.S_Atlantic_14_Free = True

    # Time of last event processed
    GlobalVar.es14w_last_event_time = current_time()

# Event handler for a car arriving at Atlantic Dr north of 14th St
def n_atlantic_s_arrival(event_data):
 # If something bad happens
    if event_data != EventType.N_ATLANTIC_S_ARRIVAL:
        print "Unexpected event type in n_atlantic_s_arrival, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "N_ATLANTIC_S_ARRIVAL Event, time = %f" % current_time()
    
    # Get identity of car
    car_identity = 'n_atlantic_s_car_%d' % (GlobalVar.n_atlantic_s_arrival_count + 1)

    # Add newly arrived car to queue to simulate arriving at intersection
    GlobalVar.n_atlantic_s_queue.enqueue(car_identity)
    
    # Update waiting time statistics
    if GlobalVar.n_atlantic_s_queue.size() > 1:
        GlobalVar.n_atlantic_s_total_waiting_time += \
            ( (GlobalVar.n_atlantic_s_queue.size() - 1) * (current_time() - GlobalVar.n_atlantic_s_last_event_time))

    # Update Statistics
    GlobalVar.NumEvents += 1
    GlobalVar.n_atlantic_s_arrival_count += 1

    # Schedule another arrival if there is still time
    # It is using a value from an exponential distribution to determine exactly when the
    # next plane is to arrive
    time = current_time()
    if time < GlobalVar.SimulationDuration:
        next_arrival = determine_next_arrival()
        # If in debug mode
        if GlobalVar.DB:
            print 'Next arrival is: ',
            print next_arrival
        new_event_type = next_arrival['event_type']
        timestamp = current_time() + rand_exp(next_arrival['mean'])
        callback = next_arrival['callback']
        simulation_engine.schedule_new_event(timestamp, new_event_type, callback)

    # Determine which direction to go, Right, Straight, or Left
    turn_direction = get_turn_direction()
    if turn_direction is "straight" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
        # Event for N_ATLANTIC_S Go Across
        # Northern and southern parts of intersection no longer free for cars to turn across
        GlobalVar.N_Atlantic_14_Free = False
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.N_ATLANTIC_S_GO_ACROSS
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_go_across)
    # Can make a left turn if no car is traversing northern part of intersection
    elif turn_direction is "left" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
        # Event for N_ATLANTIC_S Turn Left
        # This is now blocking the southern part of atlantic intersection
        GlobalVar.N_Atlantic_14_Free = False
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.N_ATLANTIC_S_TURN_LEFT
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_left)
    elif turn_direction is "right" and GlobalVar.N_Atlantic_14_Free:
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.N_ATLANTIC_S_TURN_RIGHT
        timestamp = current_time() + GlobalVar.TurnRight
        simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_right)

    # Time of last event processed
    GlobalVar.n_atlantic_s_last_event_time = current_time()

# Event handler for cars going across 14th St on Atlantic Dr
def n_atlantic_s_go_across(event_data):
    # If something bad happens
    if event_data != EventType.N_ATLANTIC_S_GO_ACROSS:
        print "Unexpected event type in n_atlantic_s_go_across, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "N_Atlantic_S Go Across event, time: %f" % current_time()
    if GlobalVar.n_atlantic_s_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from n_atlantic_s queue
    car_removed = GlobalVar.n_atlantic_s_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across N_Atlantic_S" % car_removed
        print "%d cars now in n_atlantic_s_queue" % GlobalVar.n_atlantic_s_queue.size()
        print "n_atlantic_s_queue.isEmpty() is: ",
        print GlobalVar.n_atlantic_s_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.n_atlantic_s_queue.size() > 1:
        GlobalVar.n_atlantic_s_total_waiting_time += \
        ( (GlobalVar.n_atlantic_s_queue.size() - 1) * (current_time() - GlobalVar.n_atlantic_s_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern and southern parts of intersection are now free for cars to turn across
    GlobalVar.N_Atlantic_14_Free = True
    GlobalVar.S_Atlantic_14_Free = True

    # Time of last event processed
    GlobalVar.n_atlantic_s_last_event_time = current_time()

# Event handler for cars turning left and out of the system
def n_atlantic_s_turn_left(event_data):
    # If something bad happens
    if event_data != EventType.N_ATLANTIC_S_TURN_LEFT:
        print "Unexpected event type in n_atlantic_s_turn_left, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "N_Atlantic_S Turn Left event, time: %f" % current_time()
    if GlobalVar.n_atlantic_s_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from n_atlantic_s queue
    car_removed = GlobalVar.n_atlantic_s_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went right from  N_Atlantic_S onto 14th St" % car_removed
        print "%d cars now in n_atlantic_s_queue" % GlobalVar.n_atlantic_s_queue.size()
        print "n_atlantic_s_queue.isEmpty() is: ",
        print GlobalVar.n_atlantic_s_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.n_atlantic_s_queue.size() > 1:
        GlobalVar.n_atlantic_s_total_waiting_time += \
        ( (GlobalVar.n_atlantic_s_queue.size() - 1) * (current_time() - GlobalVar.n_atlantic_s_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern and southern parts of intersection are now free for cars to turn across
    GlobalVar.N_Atlantic_14_Free = True
    GlobalVar.S_Atlantic_14_Free = True

    # Time of last event processed
    GlobalVar.n_atlantic_s_last_event_time = current_time()

# Event handler for cars turning right from Atlantic Dr onto 14th St
def n_atlantic_s_turn_right(event_data):
    # If something bad happens
    if event_data != EventType.N_ATLANTIC_S_TURN_RIGHT:
        print "Unexpected event type in n_atlantic_s_turn_right, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "N_Atlantic_S Turn Right event, time: %f" % current_time()
    if GlobalVar.n_atlantic_s_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from n_atlantic_s queue
    car_removed = GlobalVar.n_atlantic_s_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went right from  N_Atlantic_S onto 14th St" % car_removed
        print "%d cars now in n_atlantic_s_queue" % GlobalVar.n_atlantic_s_queue.size()
        print "n_atlantic_s_queue.isEmpty() is: ",
        print GlobalVar.n_atlantic_s_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.n_atlantic_s_queue.size() > 1:
        GlobalVar.n_atlantic_s_total_waiting_time += \
        ( (GlobalVar.n_atlantic_s_queue.size() - 1) * (current_time() - GlobalVar.n_atlantic_s_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern part of intersection is now free for cars to turn across
    GlobalVar.N_Atlantic_14_Free = True

    # Time of last event processed
    GlobalVar.n_atlantic_s_last_event_time = current_time()

# Event handler for a car arriving at Atlantic Dr south of 14th St
def s_atlantic_n_arrival(event_data):
 # If something bad happens
    if event_data != EventType.S_ATLANTIC_N_ARRIVAL:
        print "Unexpected event type in s_atlantic_n_arrival, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "S_ATLANTIC_N_ARRIVAL Event, time = %f" % current_time()
    
    # Get identity of car
    car_identity = 's_atlantic_n_car_%d' % (GlobalVar.s_atlantic_n_arrival_count + 1)

    # Add newly arrived car to queue to simulate arriving at intersection
    GlobalVar.s_atlantic_n_queue.enqueue(car_identity)
    
    # Update waiting time statistics
    if GlobalVar.s_atlantic_n_queue.size() > 1:
        GlobalVar.s_atlantic_n_total_waiting_time += \
            ( (GlobalVar.s_atlantic_n_queue.size() - 1) * (current_time() - GlobalVar.s_atlantic_n_last_event_time))

    # Update Statistics
    GlobalVar.NumEvents += 1
    GlobalVar.s_atlantic_n_arrival_count += 1

    # Schedule another arrival if there is still time
    # It is using a value from an exponential distribution to determine exactly when the
    # next plane is to arrive
    time = current_time()
    if time < GlobalVar.SimulationDuration:
        next_arrival = determine_next_arrival()
        # If in debug mode
        if GlobalVar.DB:
            print 'Next arrival is: ',
            print next_arrival
        new_event_type = next_arrival['event_type']
        timestamp = current_time() + rand_exp(next_arrival['mean'])
        callback = next_arrival['callback']
        simulation_engine.schedule_new_event(timestamp, new_event_type, callback)

    # Determine which direction to go, Right, Straight, or Left
    turn_direction = get_turn_direction()
    if turn_direction is "straight" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
        # Event for S_ATLANTIC_N Go Across
        # Northern and southern parts of intersection no longer free for cars to turn across
        GlobalVar.N_Atlantic_14_Free = False
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.S_ATLANTIC_N_GO_ACROSS
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_go_across)
    # Can make a left turn if no car is traversing northern part of intersection
    elif turn_direction is "left" and GlobalVar.N_Atlantic_14_Free and GlobalVar.S_Atlantic_14_Free:
        # Event for S_ATLANTIC_N Turn Left
        # This is now blocking the southern part of atlantic intersection
        GlobalVar.N_Atlantic_14_Free = False
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.S_ATLANTIC_N_TURN_LEFT
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_left)
    elif turn_direction is "right" and GlobalVar.S_Atlantic_14_Free:
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.S_ATLANTIC_N_TURN_RIGHT
        timestamp = current_time() + GlobalVar.TurnRight
        simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_right)

    # Time of last event processed
    GlobalVar.s_atlantic_n_last_event_time = current_time()

# Event handler for cars going across 14th St on Atlantic Dr
def s_atlantic_n_go_across(event_data):
    # If something bad happens
    if event_data != EventType.S_ATLANTIC_N_GO_ACROSS:
        print "Unexpected event type in s_atlantic_n_go_across, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "S_Atlantic_N Go Across event, time: %f" % current_time()
    if GlobalVar.s_atlantic_n_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from s_atlantic_n queue
    car_removed = GlobalVar.s_atlantic_n_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across S_Atlantic_N" % car_removed
        print "%d cars now in s_atlantic_n_queue" % GlobalVar.s_atlantic_n_queue.size()
        print "s_atlantic_n_queue.isEmpty() is: ",
        print GlobalVar.s_atlantic_n_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.s_atlantic_n_queue.size() > 1:
        GlobalVar.s_atlantic_n_total_waiting_time += \
        ( (GlobalVar.s_atlantic_n_queue.size() - 1) * (current_time() - GlobalVar.s_atlantic_n_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern and southern parts of intersection are now free for cars to turn across
    GlobalVar.N_Atlantic_14_Free = True
    GlobalVar.S_Atlantic_14_Free = True

    # Time of last event processed
    GlobalVar.s_atlantic_n_last_event_time = current_time()

# Event handler for cars turning left and out of the system
def s_atlantic_n_turn_left(event_data):
    # If something bad happens
    if event_data != EventType.S_ATLANTIC_N_TURN_LEFT:
        print "Unexpected event type in s_atlantic_n_turn_left, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "S_Atlantic_N Turn Left event, time: %f" % current_time()
    if GlobalVar.s_atlantic_n_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from s_atlantic_n queue
    car_removed = GlobalVar.s_atlantic_n_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went left from  S_Atlantic_N onto 14th St" % car_removed
        print "%d cars now in s_atlantic_n_queue" % GlobalVar.s_atlantic_n_queue.size()
        print "s_atlantic_n_queue.isEmpty() is: ",
        print GlobalVar.s_atlantic_n_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.s_atlantic_n_queue.size() > 1:
        GlobalVar.s_atlantic_n_total_waiting_time += \
        ( (GlobalVar.s_atlantic_n_queue.size() - 1) * (current_time() - GlobalVar.s_atlantic_n_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern and southern parts of intersection are now free for cars to turn across
    GlobalVar.N_Atlantic_14_Free = True
    GlobalVar.S_Atlantic_14_Free = True

    # Time of last event processed
    GlobalVar.s_atlantic_n_last_event_time = current_time()

# Event handler for cars turning left and out of the system
def s_atlantic_n_turn_right(event_data):
    # If something bad happens
    if event_data != EventType.S_ATLANTIC_N_TURN_RIGHT:
        print "Unexpected event type in s_atlantic_n_turn_right, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "S_Atlantic_N Turn Right event, time: %f" % current_time()
    if GlobalVar.s_atlantic_n_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from s_atlantic_n queue
    car_removed = GlobalVar.s_atlantic_n_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went right from  S_Atlantic_N onto 14th St" % car_removed
        print "%d cars now in s_atlantic_n_queue" % GlobalVar.s_atlantic_n_queue.size()
        print "s_atlantic_n_queue.isEmpty() is: ",
        print GlobalVar.s_atlantic_n_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.s_atlantic_n_queue.size() > 1:
        GlobalVar.s_atlantic_n_total_waiting_time += \
        ( (GlobalVar.s_atlantic_n_queue.size() - 1) * (current_time() - GlobalVar.s_atlantic_n_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern part of intersection is now free for cars to turn across
    GlobalVar.S_Atlantic_14_Free = True

    # Time of last event processed
    GlobalVar.s_atlantic_n_last_event_time = current_time()

# Event handler for a car arriving at northern lane of 14th street from the west, west of atlantic
# with presence of traffic light
def n14e_arrival_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.N14E_ARRIVAL_TL:
        print "Unexpected event type in n14e_arrival_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "N14E_ARRIVAL Traffic Light Event, time: %f" % current_time()
    
    # Get identity of car
    car_identity = 'n14e_car_%d' % (GlobalVar.n14e_arrival_count + 1)

    # Add newly arrived car to queue to simulate arriving at traffic light
    GlobalVar.n14e_queue.enqueue(car_identity)
    
    # Update waiting time statistics
    if GlobalVar.n14e_queue.size() > 1:
        GlobalVar.n14e_total_waiting_time += \
            ( (GlobalVar.n14e_queue.size() - 1) * (current_time() - GlobalVar.n14e_last_event_time))

    # Update Statistics
    GlobalVar.NumEvents += 1
    GlobalVar.n14e_arrival_count += 1

    # Schedule another arrival if there is still time
    # It is using a value from an exponential distribution to determine exactly when the
    # next plane is to arrive
    time = current_time()
    if time < GlobalVar.SimulationDuration:
        next_arrival = determine_next_arrival_traffic_light()
        # If in debug mode
        if GlobalVar.DB:
            print 'Next arrival is: ',
            print next_arrival
        new_event_type = next_arrival['event_type']
        timestamp = current_time() + rand_exp(next_arrival['mean'])
        callback = next_arrival['callback']
        simulation_engine.schedule_new_event(timestamp, new_event_type, callback)

    # Determine which direction to go, Right, Straight, or Left
    turn_direction = get_turn_direction()
    if (turn_direction is "straight" or turn_direction is "right") and GlobalVar._14LightGreen:
        # Event for N_14_E Go Across
        # Southern part of intersection no longer free for cars to turn across
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.N14E_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, n14e_go_across_traffic_light)
    # Can make a left turn if no car is traversing northern part of intersection
    elif turn_direction is "left" and GlobalVar.N_Atlantic_14_Free and GlobalVar._14LightGreen:
        # Event for N_14_E Turn Left
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.N14E_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, n14e_turn_left_traffic_light)

    # Time of last event processed
    GlobalVar.n14e_last_event_time = current_time()

# Event handler for cars going across atlantic dr intersection on n14e with presence of traffic light
def n14e_go_across_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.N14E_GO_ACROSS_TL:
        print "Unexpected event type in n14e_go_across_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "N14E Go Across Traffic Light event, time: %f" % current_time()
    if GlobalVar.n14e_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from n14e queue
    car_removed = GlobalVar.n14e_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across N14E" % car_removed
        print "%d cars now in n14e_queue" % GlobalVar.n14e_queue.size()
        print "n14e_queue.isEmpty() is: ",
        print GlobalVar.n14e_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.n14e_queue.size() > 1:
        GlobalVar.n14e_total_waiting_time += \
        ( (GlobalVar.n14e_queue.size() - 1) * (current_time() - GlobalVar.n14e_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Southern part of intersection is now free for cars to turn across
    GlobalVar.S_Atlantic_14_Free = True

    # Need to check if more cars need to go across this lane
    if not GlobalVar.n14e_queue.isEmpty() and GlobalVar._14LightGreen:
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.N14E_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, n14e_go_across_traffic_light)
    elif not GlobalVar.es14w_queue.isEmpty() and GlobalVar.s14e_queue.isEmpty() and GlobalVar._14LightGreen:
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.ES14W_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, es14w_turn_left_traffic_light)

    # Time of last event processed
    GlobalVar.n14e_last_event_time = current_time()

# Event handler for cars turning left from northern lane of 14st east across to Atlnatic Dr north
# with presence of traffic light
def n14e_turn_left_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.N14E_TURN_LEFT_TL:
        print "Unexpected event type in n14e_turn_left_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "N14E Turn Left Traffic Light event, time: %f" % current_time()
    if GlobalVar.n14e_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''
    
    # Remove car from n14e queue
    car_removed = GlobalVar.n14e_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across N14E" % car_removed
        print "%d cars now in n14e_queue" % GlobalVar.n14e_queue.size()
        print "n14e_queue.isEmpty() is: ",
        print GlobalVar.n14e_queue.isEmpty()
    
    # Update waiting time statistics
    if GlobalVar.n14e_queue.size() > 1:
        GlobalVar.n14e_total_waiting_time += \
        ( (GlobalVar.n14e_queue.size() - 1) * (current_time() - GlobalVar.n14e_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern part of intersection is now free for cars to turn across
    GlobalVar.N_Atlantic_14_Free = True

    # Check if any other cars in this lane need to cross intersection
    if not GlobalVar.n14e_queue.isEmpty() and GlobalVar._14LightGreen:
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.N14E_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, n14e_go_across_traffic_light)

    # Time of last event processed
    GlobalVar.n14e_last_event_time = current_time()

# Event handler for a car arriving at southern lane of 14th street from the west, west of atlantic
# with presence of traffic light
def s14e_arrival_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.S14E_ARRIVAL_TL:
        print "Unexpected event type in s14e_arrival_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "S14E_ARRIVAL Traffic Light Event: time=%f" % current_time()
    
    # Get identity of car
    car_identity = 's14e_car_%d' % (GlobalVar.s14e_arrival_count + 1)

    # Add newly arrived car to queue to simulate arriving at intersection
    GlobalVar.s14e_queue.enqueue(car_identity)
    
    # Update waiting time statistics
    if GlobalVar.s14e_queue.size() > 1:
        GlobalVar.s14e_total_waiting_time += \
            ( (GlobalVar.s14e_queue.size() - 1) * (current_time() - GlobalVar.s14e_last_event_time))

    # Update Statistics
    GlobalVar.NumEvents += 1
    GlobalVar.s14e_arrival_count += 1

    # Schedule another arrival if there is still time
    # It is using a value from an exponential distribution to determine exactly when the
    # next plane is to arrive
    time = current_time()
    if time < GlobalVar.SimulationDuration:
        next_arrival = determine_next_arrival_traffic_light()
        # If in debug mode
        if GlobalVar.DB:
            print 'Next arrival is: ',
            print next_arrival
        new_event_type = next_arrival['event_type']
        timestamp = current_time() + rand_exp(next_arrival['mean'])
        callback = next_arrival['callback']
        simulation_engine.schedule_new_event(timestamp, new_event_type, callback)

    # Determine which direction to go, Right, Straight, or Left
    turn_direction = get_turn_direction()
    if (turn_direction is "straight" or turn_direction is "left") and GlobalVar._14LightGreen:
        # Event for s14e Go Across
        # Southern part of intersection no longer free for cars to turn across
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.S14E_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, s14e_go_across_traffic_light)
    # Can make a left turn if no car is traversing northern part of intersection
    elif turn_direction is "right" and GlobalVar._14LightGreen:
        # Event for N_14_E Turn Right
        new_event_type = EventType.S14E_TURN_RIGHT_TL
        timestamp = current_time() + GlobalVar.TurnRight
        simulation_engine.schedule_new_event(timestamp, new_event_type, s14e_turn_right_traffic_light)

    # Time of last event processed
    GlobalVar.s14e_last_event_time = current_time()

# Event handler for cars going across atlantic dr intersection on s14e with presence of traffic light
def s14e_go_across_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.S14E_GO_ACROSS_TL:
        print "Unexpected event type in s14e_go_across_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "S14E Go Across Traffic Light event, time: %f" % current_time()
    if GlobalVar.s14e_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from s14e queue
    car_removed = GlobalVar.s14e_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across S14E" % car_removed
        print "%d cars now in s14e_queue" % GlobalVar.s14e_queue.size()
        print "s14e_queue.isEmpty() is: ",
        print GlobalVar.s14e_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.s14e_queue.size() > 1:
        GlobalVar.s14e_total_waiting_time += \
        ( (GlobalVar.s14e_queue.size() - 1) * (current_time() - GlobalVar.s14e_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Southern part of intersection is now free for cars to turn across
    GlobalVar.S_Atlantic_14_Free = True

    # Need to check if any other cars are waiting to cross this section of road
    if not GlobalVar.s14e_queue.isEmpty() and GlobalVar._14LightGreen:
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.S14E_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, s14e_go_across_traffic_light)
    elif not GlobalVar.es14w_queue.isEmpty() and GlobalVar.n14e_queue.isEmpty() and GlobalVar._14LightGreen:
        # Need to check if more cars need to go across this lane
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.ES14W_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, es14w_turn_left_traffic_light)

    # Time of last event processed
    GlobalVar.s14e_last_event_time = current_time()

# Event handler for cars turning right onto atlantic dr from s14e with presence of traffic light
def s14e_turn_right_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.S14E_TURN_RIGHT_TL:
        print "Unexpected event type in s14e_turn_right_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "S14E Turn Right Traffic Light event, time: %f" % current_time()
    if GlobalVar.s14e_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from s14e queue
    car_removed = GlobalVar.s14e_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went right from S14E onto Atlantic Dr south" % car_removed
        print "%d cars now in s14e_queue" % GlobalVar.s14e_queue.size()
        print "s14e_queue.isEmpty() is: ",
        print GlobalVar.s14e_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.s14e_queue.size() > 1:
        GlobalVar.s14e_total_waiting_time += \
        ( (GlobalVar.s14e_queue.size() - 1) * (current_time() - GlobalVar.s14e_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Need to see if any other cars are waiting to cross intersection in this lane
    if not GlobalVar.s14e_queue.isEmpty() and GlobalVar._14LightGreen:
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.S14E_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, s14e_go_across_traffic_light)

    # Time of last event processed
    GlobalVar.s14e_last_event_time = current_time()

# Event handler for a car arriving at northern lane of 14th street from the east, east of atlantic
# with presence of traffic light
def en14w_arrival_traffic_light(event_data):
 # If something bad happens
    if event_data != EventType.EN14W_ARRIVAL_TL:
        print "Unexpected event type in es14w_arrival_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "EN14W_ARRIVAL Traffic Light Event, time = %f" % current_time()
    
    # Get identity of car
    car_identity = 'en14w_car_%d' % (GlobalVar.en14w_arrival_count + 1)

    # Add newly arrived car to queue to simulate arriving at intersection
    GlobalVar.en14w_queue.enqueue(car_identity)
    
    # Update waiting time statistics
    if GlobalVar.en14w_queue.size() > 1:
        if GlobalVar.DB:
            print "en14w queue size greater than 1, is: %d" % GlobalVar.en14w_queue.size()
        GlobalVar.en14w_total_waiting_time += \
            ( (GlobalVar.en14w_queue.size() - 1) * (current_time() - GlobalVar.en14w_last_event_time))

    # Update Statistics
    GlobalVar.NumEvents += 1
    GlobalVar.en14w_arrival_count += 1

    # Schedule another arrival if there is still time
    # It is using a value from an exponential distribution to determine exactly when the
    # next plane is to arrive
    time = current_time()
    if time < GlobalVar.SimulationDuration:
        next_arrival = determine_next_arrival_traffic_light()
        # If in debug mode
        if GlobalVar.DB:
            print 'Next arrival is: ',
            print next_arrival
        new_event_type = next_arrival['event_type']
        timestamp = current_time() + rand_exp(next_arrival['mean'])
        callback = next_arrival['callback']
        simulation_engine.schedule_new_event(timestamp, new_event_type, callback)

    # Determine which direction to go, Right, Straight, or Left
    turn_direction = get_turn_direction()
    if (turn_direction is "straight" or turn_direction is "left") and GlobalVar._14LightGreen:
        # Event for EN14W Go Across
        # Northern part of intersection no longer free for cars to turn across
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.EN14W_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, en14w_go_across_traffic_light)
    # Can make a left turn if no car is traversing northern part of intersection
    elif turn_direction is "right" and GlobalVar._14LightGreen:
        # Event for EN14W Turn Right
        new_event_type = EventType.EN14W_TURN_RIGHT_TL
        timestamp = current_time() + GlobalVar.TurnRight
        simulation_engine.schedule_new_event(timestamp, new_event_type, en14w_turn_right_traffic_light)

    # Time of last event processed
    GlobalVar.en14w_last_event_time = current_time()

# Event handler for cars going across Atlantic Dr on EN14W with presence of traffic light
# with presence of traffic light
def en14w_go_across_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.EN14W_GO_ACROSS_TL:
        print "Unexpected event type in es14w_go_across_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "EN14W Go Across Traffic Light event, time: %f" % current_time()
    if GlobalVar.en14w_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from en14w queue
    car_removed = GlobalVar.en14w_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across EN14W" % car_removed
        print "%d cars now in en14w_queue" % GlobalVar.en14w_queue.size()
        print "en14w_queue.isEmpty() is: ",
        print GlobalVar.en14w_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.en14w_queue.size() > 1:
        GlobalVar.en14w_total_waiting_time += \
        ( (GlobalVar.en14w_queue.size() - 1) * (current_time() - GlobalVar.en14w_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern part of intersection is now free for cars to turn across
    GlobalVar.N_Atlantic_14_Free = True

    # Need to check if any other cars are waiting to cross this section of road
    if not GlobalVar.en14w_queue.isEmpty() and GlobalVar._14LightGreen:
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.EN14W_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, en14w_go_across_traffic_light)
    elif not GlobalVar.n14e_queue.isEmpty() and GlobalVar.es14w_queue.isEmpty() and GlobalVar._14LightGreen:
        # Need to check if any cars waiting to turn
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.N14E_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, n14e_turn_left_traffic_light)

    # Time of last event processed
    GlobalVar.en14w_last_event_time = current_time()

# Event handler for cars turning right onto atlantic dr from en14w with presence of traffic light
def en14w_turn_right_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.EN14W_TURN_RIGHT_TL:
        print "Unexpected event type in es14w_turn_right_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "EN14W Turn Right Traffic Light event, time: %f" % current_time()
    if GlobalVar.en14w_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from en14w queue
    car_removed = GlobalVar.en14w_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went right from EN14W onto Atlantic Dr south" % car_removed
        print "%d cars now in en14w_queue" % GlobalVar.en14w_queue.size()
        print "en14w_queue.isEmpty() is: ",
        print GlobalVar.en14w_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.en14w_queue.size() > 1:
        GlobalVar.en14w_total_waiting_time += \
        ( (GlobalVar.en14w_queue.size() - 1) * (current_time() - GlobalVar.en14w_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Need to check if any other cars are waiting to cross this section of road
    if not GlobalVar.en14w_queue.isEmpty() and GlobalVar._14LightGreen:
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.EN14W_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, en14w_go_across_traffic_light)

    # Time of last event processed
    GlobalVar.en14w_last_event_time = current_time()

# Event handler for a car arriving at southern lane of 14th street from the east, east of atlantic
# with presence of traffic light
def es14w_arrival_traffic_light(event_data):
 # If something bad happens
    if event_data != EventType.ES14W_ARRIVAL_TL:
        print "Unexpected event type in es14w_arrival_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "ES14W_ARRIVAL Traffic Light Event, time = %f" % current_time()
    
    # Get identity of car
    car_identity = 'es14w_car_%d' % (GlobalVar.es14w_arrival_count + 1)

    # Add newly arrived car to queue to simulate arriving at intersection
    GlobalVar.es14w_queue.enqueue(car_identity)
    
    # Update waiting time statistics
    if GlobalVar.es14w_queue.size() > 1:
        GlobalVar.es14w_total_waiting_time += \
            ( (GlobalVar.es14w_queue.size() - 1) * (current_time() - GlobalVar.es14w_last_event_time))

    # Update Statistics
    GlobalVar.NumEvents += 1
    GlobalVar.es14w_arrival_count += 1

    # Schedule another arrival if there is still time
    # It is using a value from an exponential distribution to determine exactly when the
    # next plane is to arrive
    time = current_time()
    if time < GlobalVar.SimulationDuration:
        next_arrival = determine_next_arrival_traffic_light()
        # If in debug mode
        if GlobalVar.DB:
            print 'Next arrival is: ',
            print next_arrival
        new_event_type = next_arrival['event_type']
        timestamp = current_time() + rand_exp(next_arrival['mean'])
        callback = next_arrival['callback']
        simulation_engine.schedule_new_event(timestamp, new_event_type, callback)

    # Determine which direction to go, Right, Straight, or Left
    turn_direction = get_turn_direction()
    if (turn_direction is "straight" or turn_direction is "right") and GlobalVar._14LightGreen:
        # Event for ES14W Go Across
        # Northern part of intersection no longer free for cars to turn across
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.ES14W_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, es14w_go_across_traffic_light)
    # Can make a left turn if no car is traversing southern part of intersection
    elif turn_direction is "left" and GlobalVar.S_Atlantic_14_Free and GlobalVar._14LightGreen:
        # Event for ES14W Turn Left
        # This is now blocking the southern part of atlantic intersection
        GlobalVar.S_Atlantic_14_Free = False
        new_event_type = EventType.ES14W_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, es14w_turn_left_traffic_light)

    # Time of last event processed
    GlobalVar.es14w_last_event_time = current_time()

# Event handler for cars going across Atlantic Dr on ES14W with presence of traffic light
def es14w_go_across_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.ES14W_GO_ACROSS_TL:
        print "Unexpected event type in es14w_go_across_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "ES14W Go Across Traffic Light event, time: %f" % current_time()
    if GlobalVar.es14w_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from es14w queue
    car_removed = GlobalVar.es14w_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across ES14W" % car_removed
        print "%d cars now in es14w_queue" % GlobalVar.es14w_queue.size()
        print "es14w_queue.isEmpty() is: ",
        print GlobalVar.es14w_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.es14w_queue.size() > 1:
        GlobalVar.es14w_total_waiting_time += \
        ( (GlobalVar.es14w_queue.size() - 1) * (current_time() - GlobalVar.es14w_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern part of intersection is now free for cars to turn across
    GlobalVar.N_Atlantic_14_Free = True

    # Need to check if any other cars are waiting to cross this section of road
    if not GlobalVar.es14w_queue.isEmpty() and GlobalVar._14LightGreen:
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.ES14W_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, es14w_go_across_traffic_light)
    elif not GlobalVar.n14e_queue.isEmpty() and GlobalVar.en14w_queue.isEmpty() and GlobalVar._14LightGreen:
        # Need to check if any cars waiting to turn
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.N14E_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, n14e_turn_left_traffic_light)

    # Time of last event processed
    GlobalVar.es14w_last_event_time = current_time()

# Event handler for cars turning left from southern lane of 14st east across to Atlnatic Dr south
# with presence of traffic light
def es14w_turn_left_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.ES14W_TURN_LEFT_TL:
        print "Unexpected event type in es14w_turn_left_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "ES14W Turn Left event, time: %f" % current_time()
    if GlobalVar.es14w_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''
    
    # Remove car from es14w queue
    car_removed = GlobalVar.es14w_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across ES14W" % car_removed
        print "%d cars now in es14w_queue" % GlobalVar.es14w_queue.size()
        print "es14w_queue.isEmpty() is: ",
        print GlobalVar.es14w_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.es14w_queue.size() > 1:
        GlobalVar.es14w_total_waiting_time += \
        ((GlobalVar.es14w_queue.size() - 1) * (current_time() - GlobalVar.es14w_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern part of intersection is now free for cars to turn across
    GlobalVar.S_Atlantic_14_Free = True

    # Need to check if any other cars are waiting to cross this section of road
    if not GlobalVar.es14w_queue.isEmpty() and GlobalVar._14LightGreen:
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.ES14W_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, es14w_go_across_traffic_light)
    elif not GlobalVar.n14e_queue.isEmpty() and GlobalVar.en14w_queue.isEmpty() and GlobalVar._14LightGreen:
        # Need to check if any cars waiting to turn
        GlobalVar.N_Atlantic_14_Free = False
        new_event_type = EventType.N14E_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, n14e_turn_left_traffic_light)

    # Time of last event processed
    GlobalVar.es14w_last_event_time = current_time()

# Event handler for a car arriving at Atlantic Dr north of 14th St with presence of traffic light
def n_atlantic_s_arrival_traffic_light(event_data):
 # If something bad happens
    if event_data != EventType.N_ATLANTIC_S_ARRIVAL_TL:
        print "Unexpected event type in n_atlantic_s_arrival_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "N_ATLANTIC_S_ARRIVAL Traffic Light Event, time = %f" % current_time()
    
    # Get identity of car
    car_identity = 'n_atlantic_s_car_%d' % (GlobalVar.n_atlantic_s_arrival_count + 1)

    # Add newly arrived car to queue to simulate arriving at intersection
    GlobalVar.n_atlantic_s_queue.enqueue(car_identity)
    
    # Update waiting time statistics
    if GlobalVar.n_atlantic_s_queue.size() > 1:
        GlobalVar.n_atlantic_s_total_waiting_time += \
            ( (GlobalVar.n_atlantic_s_queue.size() - 1) * (current_time() - GlobalVar.n_atlantic_s_last_event_time))

    # Update Statistics
    GlobalVar.NumEvents += 1
    GlobalVar.n_atlantic_s_arrival_count += 1

    # Schedule another arrival if there is still time
    # It is using a value from an exponential distribution to determine exactly when the
    # next plane is to arrive
    time = current_time()
    if time < GlobalVar.SimulationDuration:
        next_arrival = determine_next_arrival_traffic_light()
        # If in debug mode
        if GlobalVar.DB:
            print 'Next arrival is: ',
            print next_arrival
        new_event_type = next_arrival['event_type']
        timestamp = current_time() + rand_exp(next_arrival['mean'])
        callback = next_arrival['callback']
        simulation_engine.schedule_new_event(timestamp, new_event_type, callback)

    # Determine which direction to go, Right, Straight, or Left
    turn_direction = get_turn_direction()
    if turn_direction is "straight" and GlobalVar._AtlanticLightGreen and GlobalVar.W_Atlantic_14_Free:
        # Event for N_ATLANTIC_S_TL Go Across
        GlobalVar.W_Atlantic_14_Free = False
        new_event_type = EventType.N_ATLANTIC_S_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_go_across_traffic_light)
    # Can make a left turn if no car is traversing northern part of intersection
    elif turn_direction is "left" and GlobalVar._AtlanticLightGreen and GlobalVar.E_Atlantic_14_Free:
        # Event for N_ATLANTIC_S Turn Left
        # This is now blocking the southern part of atlantic intersection
        GlobalVar.E_Atlantic_14_Free = False
        new_event_type = EventType.N_ATLANTIC_S_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_left_traffic_light)
    elif turn_direction is "right" and GlobalVar._AtlanticLightGreen:
        GlobalVar.W_Atlantic_14_Free = False
        new_event_type = EventType.N_ATLANTIC_S_TURN_RIGHT_TL
        timestamp = current_time() + GlobalVar.TurnRight
        simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_right_traffic_light)

    # Time of last event processed
    GlobalVar.n_atlantic_s_last_event_time = current_time()

# Event handler for cars going across 14th St on Atlantic Dr with presence of traffic light
def n_atlantic_s_go_across_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.N_ATLANTIC_S_GO_ACROSS_TL:
        print "Unexpected event type in n_atlantic_s_go_across_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "N_Atlantic_S Go Across Traffic Light event, time: %f" % current_time()
    if GlobalVar.n_atlantic_s_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from n_atlantic_s queue
    car_removed = GlobalVar.n_atlantic_s_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across N_Atlantic_S" % car_removed
        print "%d cars now in n_atlantic_s_queue" % GlobalVar.n_atlantic_s_queue.size()
        print "n_atlantic_s_queue.isEmpty() is: ",
        print GlobalVar.n_atlantic_s_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.n_atlantic_s_queue.size() > 1:
        GlobalVar.n_atlantic_s_total_waiting_time += \
        ( (GlobalVar.n_atlantic_s_queue.size() - 1) * (current_time() - GlobalVar.n_atlantic_s_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Western part of intersection is now free for cars to turn across
    GlobalVar.W_Atlantic_14_Free = True

    # Need to check if any other cars are waiting to cross this section of road
    if not GlobalVar.n_atlantic_s_queue.isEmpty() and GlobalVar._AtlanticLightGreen:
        GlobalVar.W_Atlantic_14_Free = False
        new_event_type = EventType.N_ATLANTIC_S_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_go_across_traffic_light)
    elif not GlobalVar.s_atlantic_n_queue.isEmpty() and GlobalVar._AtlanticLightGreen:
        # Need to check if any cars waiting to turn
        GlobalVar.W_Atlantic_14_Free = False
        new_event_type = EventType.S_ATLANTIC_N_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_left_traffic_light)

    # Time of last event processed
    GlobalVar.n_atlantic_s_last_event_time = current_time()

# Event handler for cars turning left and out of the system with presence of traffic light
def n_atlantic_s_turn_left_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.N_ATLANTIC_S_TURN_LEFT_TL:
        print "Unexpected event type in n_atlantic_s_turn_left_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "N_Atlantic_S Turn Left Traffic Light event, time: %f" % current_time()
    if GlobalVar.n_atlantic_s_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from n_atlantic_s queue
    car_removed = GlobalVar.n_atlantic_s_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went right from  N_Atlantic_S onto 14th St" % car_removed
        print "%d cars now in n_atlantic_s_queue" % GlobalVar.n_atlantic_s_queue.size()
        print "n_atlantic_s_queue.isEmpty() is: ",
        print GlobalVar.n_atlantic_s_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.n_atlantic_s_queue.size() > 1:
        GlobalVar.n_atlantic_s_total_waiting_time += \
        ( (GlobalVar.n_atlantic_s_queue.size() - 1) * (current_time() - GlobalVar.n_atlantic_s_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Eastern part of intersection is now free for cars to turn across
    GlobalVar.E_Atlantic_14_Free = True

    # Need to check if any other cars are waiting to cross this section of road
    if not GlobalVar.n_atlantic_s_queue.isEmpty() and GlobalVar._AtlanticLightGreen:
        GlobalVar.W_Atlantic_14_Free = False
        new_event_type = EventType.N_ATLANTIC_S_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_go_across_traffic_light)
    elif not GlobalVar.s_atlantic_n_queue.isEmpty() and GlobalVar._AtlanticLightGreen:
        # Need to check if any cars waiting to turn
        GlobalVar.W_Atlantic_14_Free = False
        new_event_type = EventType.S_ATLANTIC_N_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_left_traffic_light)

    # Time of last event processed
    GlobalVar.n_atlantic_s_last_event_time = current_time()

# Event handler for cars turning right from Atlantic Dr onto 14th St with presence of traffic light
def n_atlantic_s_turn_right_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.N_ATLANTIC_S_TURN_RIGHT_TL:
        print "Unexpected event type in n_atlantic_s_turn_right_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "N_Atlantic_S Turn Right Traffic Light event, time: %f" % current_time()
    if GlobalVar.n_atlantic_s_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from n_atlantic_s queue
    car_removed = GlobalVar.n_atlantic_s_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went right from  N_Atlantic_S onto 14th St" % car_removed
        print "%d cars now in n_atlantic_s_queue" % GlobalVar.n_atlantic_s_queue.size()
        print "n_atlantic_s_queue.isEmpty() is: ",
        print GlobalVar.n_atlantic_s_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.n_atlantic_s_queue.size() > 1:
        GlobalVar.n_atlantic_s_total_waiting_time += \
        ( (GlobalVar.n_atlantic_s_queue.size() - 1) * (current_time() - GlobalVar.n_atlantic_s_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Northern part of intersection is now free for cars to turn across
    GlobalVar.W_Atlantic_14_Free = True

    # Need to check if any other cars are waiting to cross this section of road
    if not GlobalVar.n_atlantic_s_queue.isEmpty() and GlobalVar._AtlanticLightGreen:
        GlobalVar.W_Atlantic_14_Free = False
        new_event_type = EventType.N_ATLANTIC_S_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_go_across_traffic_light)
    elif not GlobalVar.s_atlantic_n_queue.isEmpty() and GlobalVar._AtlanticLightGreen:
        # Need to check if any cars waiting to turn
        GlobalVar.W_Atlantic_14_Free = False
        new_event_type = EventType.S_ATLANTIC_N_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_left_traffic_light)

    # Time of last event processed
    GlobalVar.n_atlantic_s_last_event_time = current_time()

# Event handler for a car arriving at Atlantic Dr south of 14th St with presence of traffic light
def s_atlantic_n_arrival_traffic_light(event_data):
 # If something bad happens
    if event_data != EventType.S_ATLANTIC_N_ARRIVAL_TL:
        print "Unexpected event type in s_atlantic_n_arrival_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "S_ATLANTIC_N_ARRIVAL Traffic Light Event, time = %f" % current_time()
    
    # Get identity of car
    car_identity = 's_atlantic_n_car_%d' % (GlobalVar.s_atlantic_n_arrival_count + 1)

    # Add newly arrived car to queue to simulate arriving at intersection
    GlobalVar.s_atlantic_n_queue.enqueue(car_identity)
    
    # Update waiting time statistics
    if GlobalVar.s_atlantic_n_queue.size() > 1:
        GlobalVar.s_atlantic_n_total_waiting_time += \
            ( (GlobalVar.s_atlantic_n_queue.size() - 1) * (current_time() - GlobalVar.s_atlantic_n_last_event_time))

    # Update Statistics
    GlobalVar.NumEvents += 1
    GlobalVar.s_atlantic_n_arrival_count += 1

    # Schedule another arrival if there is still time
    # It is using a value from an exponential distribution to determine exactly when the
    # next plane is to arrive
    time = current_time()
    if time < GlobalVar.SimulationDuration:
        next_arrival = determine_next_arrival_traffic_light()
        # If in debug mode
        if GlobalVar.DB:
            print 'Next arrival is: ',
            print next_arrival
        new_event_type = next_arrival['event_type']
        timestamp = current_time() + rand_exp(next_arrival['mean'])
        callback = next_arrival['callback']
        simulation_engine.schedule_new_event(timestamp, new_event_type, callback)

    # Determine which direction to go, Right, Straight, or Left
    turn_direction = get_turn_direction()
    if turn_direction is "straight" and GlobalVar.E_Atlantic_14_Free and GlobalVar._AtlanticLightGreen:
        # Event for S_ATLANTIC_N Go Across
        # Northern and southern parts of intersection no longer free for cars to turn across
        GlobalVar.E_Atlantic_14_Free = False
        new_event_type = EventType.S_ATLANTIC_N_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_go_across_traffic_light)
    # Can make a left turn if no car is traversing northern part of intersection
    elif turn_direction is "left" and GlobalVar.W_Atlantic_14_Free and GlobalVar._AtlanticLightGreen:
        # Event for S_ATLANTIC_N Turn Left
        GlobalVar.W_Atlantic_14_Free = False
        new_event_type = EventType.S_ATLANTIC_N_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_left_traffic_light)
    elif turn_direction is "right" and GlobalVar._AtlanticLightGreen:
        GlobalVar.E_Atlantic_14_Free = False
        new_event_type = EventType.S_ATLANTIC_N_TURN_RIGHT_TL
        timestamp = current_time() + GlobalVar.TurnRight
        simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_turn_right_traffic_light)

    # Time of last event processed
    GlobalVar.s_atlantic_n_last_event_time = current_time()

# Event handler for cars going across 14th St on Atlantic Dr with presence of traffic light
def s_atlantic_n_go_across_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.S_ATLANTIC_N_GO_ACROSS_TL:
        print "Unexpected event type in s_atlantic_n_go_across_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "S_Atlantic_N Go Across Traffic Light event, time: %f" % current_time()
    if GlobalVar.s_atlantic_n_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from s_atlantic_n queue
    car_removed = GlobalVar.s_atlantic_n_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went across S_Atlantic_N" % car_removed
        print "%d cars now in s_atlantic_n_queue" % GlobalVar.s_atlantic_n_queue.size()
        print "s_atlantic_n_queue.isEmpty() is: ",
        print GlobalVar.s_atlantic_n_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.s_atlantic_n_queue.size() > 1:
        GlobalVar.s_atlantic_n_total_waiting_time += \
        ( (GlobalVar.s_atlantic_n_queue.size() - 1) * (current_time() - GlobalVar.s_atlantic_n_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Eastern part of intersection is now free for cars to turn across
    GlobalVar.E_Atlantic_14_Free = True

    # Need to check if any other cars are waiting to cross this section of road
    if not GlobalVar.s_atlantic_n_queue.isEmpty() and GlobalVar._AtlanticLightGreen:
        GlobalVar.E_Atlantic_14_Free = False
        new_event_type = EventType.S_ATLANTIC_N_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_go_across_traffic_light)
    elif not GlobalVar.n_atlantic_s_queue.isEmpty() and GlobalVar._AtlanticLightGreen:
        # Need to check if any cars waiting to turn
        GlobalVar.E_Atlantic_14_Free = False
        new_event_type = EventType.N_ATLANTIC_S_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_left_traffic_light)

    # Time of last event processed
    GlobalVar.s_atlantic_n_last_event_time = current_time()

# Event handler for cars turning left and out of the system with presence of traffic light
def s_atlantic_n_turn_left_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.S_ATLANTIC_N_TURN_LEFT_TL:
        print "Unexpected event type in s_atlantic_n_turn_left_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "S_Atlantic_N Turn Left Traffic Light event, time: %f" % current_time()
    if GlobalVar.s_atlantic_n_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from s_atlantic_n queue
    car_removed = GlobalVar.s_atlantic_n_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went left from  S_Atlantic_N onto 14th St" % car_removed
        print "%d cars now in s_atlantic_n_queue" % GlobalVar.s_atlantic_n_queue.size()
        print "s_atlantic_n_queue.isEmpty() is: ",
        print GlobalVar.s_atlantic_n_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.s_atlantic_n_queue.size() > 1:
        GlobalVar.s_atlantic_n_total_waiting_time += \
        ( (GlobalVar.s_atlantic_n_queue.size() - 1) * (current_time() - GlobalVar.s_atlantic_n_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Western parts of intersection is now free for cars to turn across
    GlobalVar.W_Atlantic_14_Free = True

    # Need to check if any other cars are waiting to cross this section of road
    if not GlobalVar.s_atlantic_n_queue.isEmpty() and GlobalVar._AtlanticLightGreen:
        GlobalVar.E_Atlantic_14_Free = False
        new_event_type = EventType.S_ATLANTIC_N_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_go_across_traffic_light)
    elif not GlobalVar.n_atlantic_s_queue.isEmpty() and GlobalVar._AtlanticLightGreen:
        # Need to check if any cars waiting to turn
        GlobalVar.E_Atlantic_14_Free = False
        new_event_type = EventType.N_ATLANTIC_S_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_left_traffic_light)

    # Time of last event processed
    GlobalVar.s_atlantic_n_last_event_time = current_time()

# Event handler for cars turning left and out of the system
def s_atlantic_n_turn_right_traffic_light(event_data):
    # If something bad happens
    if event_data != EventType.S_ATLANTIC_N_TURN_RIGHT_TL:
        print "Unexpected event type in s_atlantic_n_turn_right_traffic_light, type is %d" % event_data
        sys.exit()
    # If in debug mode
    if GlobalVar.DB:
        print "S_Atlantic_N Turn Right Traffic Light event, time: %f" % current_time()
    if GlobalVar.s_atlantic_n_queue.isEmpty():
        if GlobalVar.DB:
            print "Already handled, returning"
        return ''

    # Remove car from s_atlantic_n queue
    car_removed = GlobalVar.s_atlantic_n_queue.dequeue()
    # If in debug mode
    if GlobalVar.DB:
        print "%s went right from  S_Atlantic_N onto 14th St" % car_removed
        print "%d cars now in s_atlantic_n_queue" % GlobalVar.s_atlantic_n_queue.size()
        print "s_atlantic_n_queue.isEmpty() is: ",
        print GlobalVar.s_atlantic_n_queue.isEmpty()

    # Update waiting time statistics
    if GlobalVar.s_atlantic_n_queue.size() > 1:
        GlobalVar.s_atlantic_n_total_waiting_time += \
        ( (GlobalVar.s_atlantic_n_queue.size() - 1) * (current_time() - GlobalVar.s_atlantic_n_last_event_time))

    # Update experiment statistics
    GlobalVar.NumEvents = GlobalVar.NumEvents + 1

    # Eastern part of intersection is now free for cars to turn across
    GlobalVar.E_Atlantic_14_Free = True

    # Need to check if any other cars are waiting to cross this section of road
    if not GlobalVar.s_atlantic_n_queue.isEmpty() and GlobalVar._AtlanticLightGreen:
        GlobalVar.E_Atlantic_14_Free = False
        new_event_type = EventType.S_ATLANTIC_N_GO_ACROSS_TL
        timestamp = current_time() + GlobalVar.GoAcross
        simulation_engine.schedule_new_event(timestamp, new_event_type, s_atlantic_n_go_across_traffic_light)
    elif not GlobalVar.n_atlantic_s_queue.isEmpty() and GlobalVar._AtlanticLightGreen:
        # Need to check if any cars waiting to turn
        GlobalVar.E_Atlantic_14_Free = False
        new_event_type = EventType.N_ATLANTIC_S_TURN_LEFT_TL
        timestamp = current_time() + GlobalVar.TurnLeft
        simulation_engine.schedule_new_event(timestamp, new_event_type, n_atlantic_s_turn_left_traffic_light)

    # Time of last event processed
    GlobalVar.s_atlantic_n_last_event_time = current_time()

# This is the main driver of the simulation, this is where we kick things off
def intersection_simulation():
    # To start off the experiment, need to schedule a new arrival event
    if GlobalVar.TrafficLight:
        next_arrival = determine_next_arrival_traffic_light()
    else:
        next_arrival = determine_next_arrival()

    # If in debug mode
    if GlobalVar.DB:
        print 'The first arrival is: ',
        print next_arrival

    # Need to schedule time for light to change
    timestamp = current_time() + GlobalVar.GreenLightDuration
    new_event_type = EventType._14_LIGHT_TURNS_RED
    simulation_engine.schedule_new_event(timestamp, new_event_type, _14_light_turns_red)

    timestamp = rand_exp(next_arrival['mean'])
    new_event_type = next_arrival['event_type']
    callback = next_arrival['callback']
    simulation_engine.schedule_new_event(timestamp, new_event_type, callback)

    if GlobalVar.DB:
        print 'Initial future event list: ',
        simulation_engine.print_future_event_list()
        print ''
    start_time = time.clock()

    # The actual execution of the simulation, with the scheduling, 
    # execution of, and then removal of the different events that transpire
    removed_event = simulation_engine.remove_event()
    # If in debug mode
    if GlobalVar.DB:
        print simulation_engine.print_future_event_list()
        print ''
    while removed_event is not None:
        GlobalVar.Now = removed_event.get_timestamp()
        callback = removed_event.get_callback()
        removed_event_type = removed_event.get_event_data()
        callback(removed_event_type)
        removed_event = simulation_engine.remove_event()
        # If in debug mode
        if GlobalVar.DB:
            print simulation_engine.print_future_event_list()
            print 'Current time: %f' % current_time()
            print ''

    end_time = time.clock()

    # print final statistics
    print '\nHere are the simulation statistics:'
    print '  Number of cars that went through n14e = %d' % GlobalVar.n14e_arrival_count
    if GlobalVar.DB:
        print '  n14e total waiting time: %f' % GlobalVar.n14e_total_waiting_time
    if GlobalVar.n14e_arrival_count != 0:
        print '  n14e average waiting time: %f' % (GlobalVar.n14e_total_waiting_time / GlobalVar.n14e_arrival_count)

    print '  Number of cars that went through s14e = %d' % GlobalVar.s14e_arrival_count
    if GlobalVar.DB:
        print '  s14e total waiting time: %f' % GlobalVar.s14e_total_waiting_time
    if GlobalVar.s14e_arrival_count != 0:
        print '  s14e average waiting time: %f' % (GlobalVar.s14e_total_waiting_time / GlobalVar.s14e_arrival_count)

    print '  Number of cars that went through en14w = %d' % GlobalVar.en14w_arrival_count
    if GlobalVar.DB:
        print '  en14w total waiting time: %f' % GlobalVar.en14w_total_waiting_time
    if GlobalVar.en14w_arrival_count != 0:
        print '  en14w average waiting time: %f' % (GlobalVar.en14w_total_waiting_time / GlobalVar.en14w_arrival_count)

    print '  Number of cars that went through es14w = %d' % GlobalVar.es14w_arrival_count
    if GlobalVar.DB:
        print '  es14w total waiting time: %f' % GlobalVar.es14w_total_waiting_time
    if GlobalVar.es14w_arrival_count != 0:
        print '  es14w average waiting time: %f' % (GlobalVar.es14w_total_waiting_time / GlobalVar.es14w_arrival_count)

    print '  Number of cars that went through n_atlantic_s = %d' % GlobalVar.n_atlantic_s_arrival_count
    if GlobalVar.DB:
        print '  n_atlantic_s total waiting time: %f' % GlobalVar.n_atlantic_s_total_waiting_time
    if GlobalVar.n_atlantic_s_arrival_count != 0:
        print '  n_atlantic_s average waiting time: %f' % (GlobalVar.n_atlantic_s_total_waiting_time / GlobalVar.n_atlantic_s_arrival_count)

    print '  Number of cars that went through s_atlantic_n = %d' % GlobalVar.s_atlantic_n_arrival_count
    if GlobalVar.DB:
        print '  s_atlantic_n total waiting time: %f' % GlobalVar.s_atlantic_n_total_waiting_time
    if GlobalVar.s_atlantic_n_arrival_count != 0:
        print '  s_atlantic_n average waiting time: %f' % (GlobalVar.s_atlantic_n_total_waiting_time / GlobalVar.s_atlantic_n_arrival_count)

    # Write statistics to csv file
    fh = open('ExperimentResults/light_g35_r13_fpoint1_a6.csv', 'a+')
    experiment_statistics = str(GlobalVar.n14e_mean_arrival) + ',' + \
                    str(GlobalVar.n_atlantic_s_mean_arrival) + ',' + \
                    str(GlobalVar.TrafficLight) + ',' + \
                    str(GlobalVar.GreenLightDuration) + ',' + \
                    str(GlobalVar.RedLightDuration) + ',' + \
                    str(GlobalVar.n14e_arrival_count) + ',' + \
                    str(GlobalVar.s14e_arrival_count) + ',' + \
                    str(GlobalVar.en14w_arrival_count) + ',' + \
                    str(GlobalVar.es14w_arrival_count) + ',' + \
                    str(GlobalVar.n_atlantic_s_arrival_count) + ',' + \
                    str(GlobalVar.s_atlantic_n_arrival_count) + ',' + \
                    str(GlobalVar.n14e_total_waiting_time / GlobalVar.n14e_arrival_count) + ',' + \
                    str(GlobalVar.s14e_total_waiting_time / GlobalVar.s14e_arrival_count) + ',' + \
                    str(GlobalVar.en14w_total_waiting_time / GlobalVar.en14w_arrival_count) + ',' + \
                    str(GlobalVar.es14w_total_waiting_time / GlobalVar.es14w_arrival_count) + ',' + \
                    str(GlobalVar.n_atlantic_s_total_waiting_time / GlobalVar.n_atlantic_s_arrival_count) + ',' + \
                    str(GlobalVar.s_atlantic_n_total_waiting_time / GlobalVar.s_atlantic_n_arrival_count) + '\n'
    fh.writelines(experiment_statistics)
    fh.close()

intersection_simulation()