import random

def shouldTriggerEvent(timestep, timesPerMinute):
    # Calculate the probability of the event occurring on this call
    probability = (timesPerMinute * timestep) / 60
    # Generate a random number and determine if the event should occur
    return random.random() <= probability

def calculateDistanceMargin(speed: float) -> float:
    speeds = [0.0, 40 / 3.6, 60 / 3.6, 80 / 3.6, 120 / 3.6]
    distances = [2.0, 5.0, 10.0, 16.0, 32.0]
    minIndex = None
    maxIndex = None
    for i, referenceSpeed in enumerate(speeds):
        if speed <= referenceSpeed:
            minIndex = i - 1
            maxIndex = i
            break
    if minIndex is not None and maxIndex is not None:
        k = (distances[maxIndex] - distances[minIndex]) / (speeds[maxIndex] - speeds[minIndex])
        b = distances[minIndex] - k * speeds[minIndex]
        return k * speed + b
    result = distances[-1]
    return result

