class EnergyPoint:
    def __init__(self):
        self.timestamp = None
        self.energy = 0.0
        self.power = 0.0

    def __str__(self):
        return f'{self.timestamp.__str__()}, {self.energy} kWh, {self.power} W'

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp
    
    def set_energy(self, energy):
        self.energy = energy
        self.power = energy * 1000 * 4