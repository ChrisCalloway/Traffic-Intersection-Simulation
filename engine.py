from future_event_list import FutureEventList
from future_event_list import Event

class SimulationEngine:
    def __init__(self):
        self.future_event_list = FutureEventList()
        self.now = 0.0
    
    # Keeps track of current time
    def current_time():
        return now

    # Wrapper method to add newly scheduled event to future event list 
    # and insert it according to timestamp
    def schedule_new_event(self, timestamp, event_data, callback):
        self.future_event_list.add_event(timestamp, event_data, callback)

    # Wrapper method to remove the first event from the future event list
    def remove_event(self):
        return self.future_event_list.remove_first_event()

    # Wrapper method to see if the future event list is empty
    def is_empty(self):
        return self.future_event_list.is_empty()

    # Wrapper method to get number of events in future event list
    def get_fel_size(self):
        return self.future_event_list.get_fel_size()

    # Wrapper method to print the current future event list
    def print_future_event_list(self):
        self.future_event_list.print_fel_list()

def simulate_this_engine():
    print 'in engine.py'
    # Initialize future event list
    future_event_list = SimulationEngine()
    future_event_list.schedule_new_event(31, None, None)
    future_event_list.schedule_new_event(77, None, None)
    future_event_list.schedule_new_event(17, None, None)
    future_event_list.schedule_new_event(93, None, None)
    future_event_list.print_future_event_list()

    print "First event removed from future event list: ",
    print future_event_list.remove_event().get_timestamp()
    future_event_list.print_future_event_list()

# simulate_this_engine()

# run_simulation()