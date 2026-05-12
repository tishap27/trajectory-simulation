from motor import Motor
from rocket import Rocket
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd

motor = Motor.load_from_eng("Cesaroni_9977M2245-P.eng")

rocket = Rocket(motor=motor, Cd=0.77, reference_area=0.009)

dt = 0.01 

trajectory = []

times = []

altitudes = []

velocities = []

machs = []

thrusts = []

while True:
    rocket.update(dt)
    
    times.append(rocket.time)
    altitudes.append(rocket.position[2])
    
    speed = np.linalg.norm(rocket.velocity)
    velocities.append(speed)

    wind_vec = rocket.wind(rocket.position)
    v_relative = rocket.velocity - wind_vec
    speed_rel = np.linalg.norm(v_relative)

    a = rocket.speed_of_sound(rocket.position[2])
    Mach = speed_rel / a
    machs.append(Mach)
    
    thrust = rocket.motor.get_thrust(rocket.time)
    thrusts.append(thrust)

    trajectory.append(rocket.position.copy())

    if rocket.position[2] < 0:
        break
     
    
    

print("Max Altitude:", max(p[2] for p in trajectory))
print("Flight time:", rocket.time)

T_max = max(motor.thrusts)
m0= rocket.dry_mass + rocket.prop_mass
print("T/W:", T_max / (m0 * 9.81))

df = pd.read_csv("Flight Test.CSV")

real_time = df["Time (sec)"]
real_time = real_time - real_time.iloc[0]


real_alt = df["Altitude (ft)"] * 0.3048
real_vel = df["Velocity (ft/sec)"] * 0.3048
real_thrust = df["Thrust (lb)"] * 4.44822

real_mach = df["Mach Number"]

real_cd = df["CD"]
real_drag = df["Drag (lb)"] * 4.44822


plt.plot(times, altitudes, label="Sim", color="blue")
plt.plot(real_time, real_alt, label="Real", color="red")
plt.legend()
plt.xlabel("Time (s)")
plt.ylabel("Altitude (m)")
plt.title("Altitude over Time")
plt.grid()

plt.figure()
plt.plot(times, velocities, label="Sim", color="blue")
plt.plot(real_time, real_vel, label ="Real", color="red")
plt.legend()
plt.xlabel("Time (s)")
plt.ylabel("Velocity (m/s)")
plt.title("Velocity over Time")
plt.grid()

plt.figure()
plt.plot(times, machs, label="Sim", color="blue")
plt.plot(real_time, real_mach, label="Real", color="red")
plt.legend()
plt.xlabel("Time (s)")
plt.ylabel("Mach")
plt.title("Mach over Time")
plt.grid()

plt.figure()
plt.plot(times, thrusts, label="Sim", color="blue")
plt.plot(real_time, real_thrust, label="Real", color="red")
plt.legend()
plt.xlabel("Time (s)")
plt.ylabel("Thrust")
plt.title("Thrust over Time")
plt.grid()

print(df["Altitude (ft)"].describe())
plt.show()
