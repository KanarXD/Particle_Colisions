import simulation
import multiprocessing

WIDTH, HEIGHT = 1000, 1000
FPS = 30
ParticleRadius = 16
ParticleSpeed = 1.0
SIMULATIONTIME = 300
ThreadCount = 10
ParticleCount_MIN = 10
ParticleCount_MAX = 100
ParticleCount_STEP = 10


def doTest(particles):
    # create result file
    file = open(f"results/result{particles},{SIMULATIONTIME}.txt", "w")
    file.write("collisions;distance\n")
    file.close()
    # create threads
    threads = []
    for i in range(ThreadCount):
        windowed = False
        if i == 0:
            windowed = True
        threads.append(multiprocessing.Process(target=simulation.run_simulation, args=(
            i, WIDTH, HEIGHT, ParticleRadius, particles, ParticleSpeed, SIMULATIONTIME, FPS, windowed,)))
    # start threads
    for i in range(ThreadCount):
        threads[i].start()
    # wait for threads
    for i in range(ThreadCount):
        threads[i].join()
    print(f"Test Particles: {particles} Done!")


if __name__ == '__main__':
    for i in range(ParticleCount_MIN, ParticleCount_MAX + ParticleCount_STEP, ParticleCount_STEP):
        doTest(i)
