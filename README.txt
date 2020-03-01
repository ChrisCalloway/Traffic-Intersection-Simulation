The intersection simulation runs on Python 2.x. To run this simulation in Deepthought, enter:
    python intersection_simulation.py

The simulation has five flag options that can be used to alter the simulation run. They are as follows:

    "-d", "--debugmode" <0, 1> - Enables a trace of the program if flag set to 1. By default, is set to 0.
    Example:
        python intersection_simulation.py -d 1

    "-a", "--atlantic" <float> - Sets mean arrival rate of cars on Atlantic Drive. By default, is set to 6.
    Example:
        python intersection_simulation.py -a 10

    "-f", "--fourteenth" <float> - Sets mean arrival rate of cars on 14th Street. By default, is set to 0.1.
    Example:
        python intersection_simulation.py -f 0.5

    "-l", "--light" <boolean> - If value passed in is true (t and True also accepted), a traffic light is used
    in the simulation. If any other value is passed in, no traffic light is used. The default value is false, so 
    no traffic light is used by default.
    Example:
        python intersection_simulation.py -l true

    "-g", "--greenlighttime" <number> - Sets the time duration the 14 St traffic light is green (and therefore
    the Atlantic Dr traffic light is red). By default, this value is 45. Only numerical digits accepted by this flag.
    Example:
        python intersection_simulation.py -g 30

    "-r", "--redlighttime" <number> - Sets the time duration the 14 St traffic light is red (and therefore
    the Atlantic Dr traffic light is green). By default, this value is 30. Only numerical digits accepted by this flag.
    Example:
        python intersection_simulation.py -r 20

    "-t", "--simtime" <number> - Sets the duration time of the simulation. By default, this value is 500. Only 
    numerical digits accepted by this flag.
    Example:
        python intersection_simulation.py -t 150

Any combination of the above flags can be used, but note if user does not set traffic light to true but sets green or red light time,
there will be no effect on the simulation.

Example with traffic light set to true and red light/green light duration set:
     python intersection_simulation.py -l true -g 30 -r 30 -t 400

Sample Output using above flags:
    Welcome to the 14St, Atlantic Dr Intersection Simulation

    Here are the simulation parameters:
        Traffic light used: True
        Green light time: 30
        Red light time: 30
        Debug mode: 0
        Simulation duration: 400

    Here are the simulation statistics:
        Number of cars that went through n14e = 110
        n14e average waiting time: 13.739015
        Number of cars that went through s14e = 91
        s14e average waiting time: 14.607459
        Number of cars that went through en14w = 89
        en14w average waiting time: 11.728712
        Number of cars that went through es14w = 100
        es14w average waiting time: 14.108780
        Number of cars that went through n_atlantic_s = 28
        n_atlantic_s average waiting time: 4.807275
        Number of cars that went through s_atlantic_n = 24
        s_atlantic_n average waiting time: 9.764776

Example with no traffic light used and red light/green light duration set:
    python2 intersection_simulation.py -g 30 -r 30 -t 400

Sample Output using above flags:
    Welcome to the 14St, Atlantic Dr Intersection Simulation

    Here are the simulation parameters:
        Traffic light used: False
        Debug mode: 0
        Simulation duration: 400

    Here are the simulation statistics:
        Number of cars that went through n14e = 134
        n14e average waiting time: 1.334012
        Number of cars that went through s14e = 130
        s14e average waiting time: 1.160292
        Number of cars that went through en14w = 121
        en14w average waiting time: 1.128215
        Number of cars that went through es14w = 156
        es14w average waiting time: 1.349442
        Number of cars that went through n_atlantic_s = 27
        n_atlantic_s average waiting time: 2.748005
        Number of cars that went through s_atlantic_n = 26
        s_atlantic_n average waiting time: 6.496348