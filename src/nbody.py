from mapper import gpumap
from util import get_time

from random import uniform
import pickle
import math


class Body:
    def __init__(self, x, y, z, vx, vy, vz, mass):
        self.pos = Vector3(x, y, z)
        self.vel = Vector3(vx, vy, vz)
        self.mass = mass


class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def add(self, other):
        return Vector3(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    def sub(self, other):
        return Vector3(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )

    def scale(self, scalar):
        return Vector3(
            scalar * self.x,
            scalar * self.y,
            scalar * self.z
        )

    def length(self):
        return math.sqrt(
            math.pow(self.x, 2) +
            math.pow(self.y, 2) +
            math.pow(self.z, 2)
        )


class BodyGenerator:
    def __init__(self, num_bodies):
        self.bodies = None
        self.num_bodies = num_bodies
        self.pickled_bodies = None

    def generate_bodies(self):
        rand_pos = lambda: uniform(-1000, 1000)
        rand_vel = lambda: uniform(-10, 10)
        rand_mass = lambda: uniform(-20, 20)
        self.bodies = [
            Body(rand_pos(), rand_pos(), rand_pos(),
                 rand_vel(), rand_vel(), rand_vel(),
                 rand_mass()) for _ in range(self.num_bodies)
            ]
        self.pickled_bodies = pickle.dumps(self.bodies)

    def get_copy(self):
        return pickle.loads(self.pickled_bodies)

class Simulation:
    def __init__(self, bodies, num_steps):
        self.bodies = bodies
        self.indices = list(range(len(bodies)))
        self.dt = 0.01
        self.num_steps = num_steps

    def advance(self, dt):
        pass

    def run(self):
        for _ in range(self.num_steps):
            self.advance(self.dt)


class GPU_Simulation(Simulation):
    def advance(self, dt):
        bodies = self.bodies

        def calc_vel(i):
            b1 = bodies[i]
            for b2 in bodies:
                d_pos = b1.pos.sub(b2.pos)
                distance = d_pos.length() + 0.0000001
                mag = dt / math.pow(distance, 3)
                b1.vel = b1.vel.sub(d_pos.scale(b2.mass).scale(mag))

        gpumap(calc_vel, self.indices)

        def update(body):
            body.pos = body.pos.add(body.vel.scale(dt))

        gpumap(update, bodies)


class CPU_Simulation(Simulation):
    def advance(self, dt):
        bodies = self.bodies

        def calc_vel(i):
            b1 = bodies[i]
            for b2 in bodies:
                d_pos = b1.pos.sub(b2.pos)
                distance = d_pos.length() + 0.0000001
                mag = dt / math.pow(distance, 3)
                b1.vel = b1.vel.sub(d_pos.scale(b2.mass).scale(mag))

        list(map(calc_vel, self.indices))

        def update(body):
            body.pos = body.pos.add(body.vel.scale(dt))

        list(map(update, bodies))


if __name__ == "__main__":
    num_steps = 10
    with open("output-10steps.csv", "w") as f:
        print("num_bodies,gpu_time,cpu_time", file=f)
        num_bodies = 2
        while num_bodies < 10000:
            print("num bodies", num_bodies)
            body_gen = BodyGenerator(num_bodies)
            body_gen.generate_bodies()

            gpu_sim = GPU_Simulation(body_gen.get_copy(), num_steps)
            gpu_time = get_time(gpu_sim.run)

            cpu_sim = CPU_Simulation(body_gen.get_copy(), num_steps)
            cpu_time = get_time(cpu_sim.run)
            print("{},{},{}".format(num_bodies, gpu_time, cpu_time), file=f)
            f.flush()
            num_bodies *= 2
