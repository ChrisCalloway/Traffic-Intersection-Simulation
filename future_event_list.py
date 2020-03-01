# Implementation of event object for future event list (modified linked list)
class Event:
    # Constructor method
    def __init__(self, timestamp, event_data, callback, next_event):
        self.timestamp = timestamp  # timestamp of when event scheduled
        self.event_data = event_data    # the kind of event scheduled
        self.callback = callback    # the function to invoke when event is executed, i.e., arrival()
        self.next_event = next_event    # a reference to the next event in the future event list

    # Get timestamp for an event in a future event list
    def get_timestamp(self):
        return self.timestamp

    # Get event_data for an event in a future event list
    def get_event_data(self):
        return self.event_data

    # Get callback function for the event
    def get_callback(self):
        return self.callback

    # Gets the refernce to an event's next event
    def get_next_event(self):
        return self.next_event

    # Create reference to the next event in future event list
    def set_next_event(self, next_event):
        self.next_event = next_event

# Implementation of future event list
class FutureEventList:
    def __init__(self):
        # This is a reference to the first event in the future event list
        self.head = None
    
    # Method to check to see if FutureEventList is empty
    def is_empty(self):
        return self.head is None

    # Method to add a new event to the future event list
    def add_event(self, timestamp, event_data, callback):
        current_event = self.head
        previous_event = None
        stop = False
        while current_event is not None and not stop:
            # If spot found where current event's timestamp is 
            # greater than or equal to this timestamp, stop
            if current_event.get_timestamp() >= timestamp:
                stop = True
            # Keep iterating if not found
            else:
                previous_event = current_event
                current_event = current_event.get_next_event()
        # Once spot to insert event is found
        temp_event = Event(timestamp, event_data, callback, None)
        # Adding event if future event list is empty, or event goes at front
        # of future event list
        if previous_event is None:
            temp_event.set_next_event(self.head)
            self.head = temp_event
        # Adding event if current position is at middle or end of future event list
        else:
            temp_event.set_next_event(current_event)
            previous_event.set_next_event(temp_event)
    
    # Removes and returns first event in future event list
    def remove_first_event(self):
        if self.head is None:
            return None
        else:
            removed_event = self.head
            new_head = self.head.get_next_event()
            self.head = new_head
            return removed_event
    
    # Gets a count of the size of the list
    def get_fel_size(self):
        print "in get_fel_size",
        current_event = self.head
        count = 0
        while current_event is not None:
            print "in get_fel_size while loop",
            count += 1
            current_event = current_event.get_next_event()
        return count

    # Prints to console the future event list
    def print_fel_list(self):
        current_event = self.head
        print "Future Event List: | ",
        while current_event is not None:
            print current_event.get_timestamp(),
            print " | ",
            current_event = current_event.get_next_event()
        print ''

def simulate_future_event_list():
    print 'in future_event_list.py'
    # Initialize future event list
    future_event_list = FutureEventList()
    future_event_list.add_event(31, None, None)
    future_event_list.add_event(77, None, None)
    future_event_list.add_event(17, None, None)
    future_event_list.add_event(93, None, None)
    future_event_list.print_fel_list()

    # future_event_list.remove_event(31)
    # future_event_list.print_fel_list()
    print "First event removed from list: ",
    print future_event_list.remove_first_event().get_timestamp()
    future_event_list.print_fel_list()

# simulate_future_event_list()