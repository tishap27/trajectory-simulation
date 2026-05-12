import numpy as np

class Motor:
    def __init__(self, name, prop_mass, total_mass, times, thrusts):
        self.name = name
        self.prop_mass = prop_mass
        self.total_mass = total_mass

        self.times = np.array(times, dtype=float)
        self.thrusts = np.array(thrusts, dtype=float)

        self.burn_time = self.times[-1]
        self.current_index = 0  # for fast lookup

    @staticmethod
    def load_from_eng(file_path):
        with open(file_path, "r") as f:
            lines = f.readlines()

        # Clean lines
        clean_lines = []
        for line in lines:
            line = line.strip()
            if line == "" or line.startswith(";"):
                continue
            clean_lines.append(line)

        # Header
        header = clean_lines[0].split()
        name = header[0]
        prop_mass = float(header[4])
        total_mass = float(header[5])

        # Thrust data
        times = []
        thrusts = []

        for line in clean_lines[1:]:
            t, F = line.split()
            times.append(float(t))
            thrusts.append(float(F))

        # Ensure starts at (0,0)
        if times[0] != 0.0:
            times.insert(0, 0.0)
            thrusts.insert(0, 0.0)

        # Ensure ends at 0 thrust
        if thrusts[-1] != 0.0:
            times.append(times[-1])
            thrusts.append(0.0)

        return Motor(name, prop_mass, total_mass, times, thrusts)

    def get_thrust(self, time):
        if time <= 0:
            return self.thrusts[0]

        if time >= self.burn_time:
            return 0.0

        # Advance index (efficient lookup)
        while (
            self.current_index < len(self.times) - 2
            and time > self.times[self.current_index + 1]
        ):
            self.current_index += 1

        i = self.current_index

        t1 = self.times[i]
        t2 = self.times[i + 1]
        F1 = self.thrusts[i]
        F2 = self.thrusts[i + 1]

        # Linear interpolation
        return F1 + (time - t1) / (t2 - t1) * (F2 - F1)