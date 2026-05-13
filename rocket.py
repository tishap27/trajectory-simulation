import numpy as np
import math

class Rocket:
    def __init__(self, motor, Cd, reference_area):
        self.position = np.array([0.0, 0.0, 0.0])
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.orientation = np.array([0.0, 0.0, 1.0])

        self.motor = motor
        self.reference_area = reference_area

        self.time = 0.0
        self.Cd = Cd

        # Mass breakdown
        self.prop_mass = motor.prop_mass
        self.dry_mass = motor.total_mass - motor.prop_mass

        self.Isp = 220

    def air_density(self, altitude):
        p = 1.225
        h = altitude 
        H = 8500   
        return p * math.exp(-h / H)

    def wind(self, position):
        return np.array([0.0, 0.0, 0.0])
    
    def speed_of_sound(self, altitude):
        return 343 - 0.003 * altitude
    
    def compute_Cd(self, Mach):
        Cd0 = self.Cd
        delta_Cd = 0.25 
        width = 0.3
        return Cd0 + delta_Cd * np.exp(-((Mach - 1) / width)**2)

    def compute_drag(self, v_relative, Mach):
        speed = np.linalg.norm(v_relative)

        if speed > 0:
            drag_dir = -v_relative / speed
        else:
            drag_dir = np.array([0.0, 0.0, 0.0])

        rho = self.air_density(self.position[2])
        Cd = self.compute_Cd(Mach)

        Fd = 0.5 * rho * Cd * self.reference_area * speed**2
        return Fd * drag_dir

    def update(self, dt):
        self.time += dt 

        mass = self.dry_mass + self.prop_mass

        # --- Thrust ---
        thrust_mag = self.motor.get_thrust(self.time)
        
        if self.prop_mass <= 0:
            thrust_mag = 0 

        mdot = thrust_mag / (self.Isp * 9.81)
        F_thrust = self.orientation * thrust_mag

        # --- Gravity ---
        g = np.array([0.0, 0.0, -9.81])
        F_gravity = mass * g

        # --- Wind ---
        wind_vec = self.wind(self.position)
       
         # --- Drag ---
        v_relative = self.velocity - wind_vec

        speed = np.linalg.norm(v_relative)
        a = self.speed_of_sound(self.position[2])
        Mach = speed / a

        F_drag = self.compute_drag(v_relative, Mach)
        
        rho = self.air_density(self.position[2])

        speed = np.linalg.norm(self.velocity)
        q = 0.5 * rho * speed**2
        
        if self.time % 1.0 < dt:
           print("Mach:", Mach)

        # --- Net force ---
        F_total = F_thrust + F_gravity + F_drag

        # --- Acceleration ---
        acc = F_total / mass

        # --- Integrate ---
        self.velocity += acc * dt
        self.position += self.velocity * dt

        fuel_used = min(self.prop_mass, mdot * dt)
        self.prop_mass = max(0, self.prop_mass - fuel_used)