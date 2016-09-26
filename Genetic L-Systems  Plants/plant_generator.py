# Author: Aleksandr Parfenov
# This is the implementation of D0L-system plant generator with genetic selection among resulted plants
# Original paper "On Genetic Algorithms and Lindenmayer Systems"
# The paper was writen by Gabriela Ochoa (COGS – School of Cognitive and Computing Sciences; The University of Sussex)

import turtle
import random

# Turtle drawer configuration. Also have effect on resulted species and it's fitness
drawer_step = 7
drawer_angle = 25

# Weights for fitness function, for following criteria list
# a) Positive phototropism
# b) Bilateral Symmetry
# c) Light gathering ability
# d) Structural stability
# e) Proportion of branching points
w = (10, 1, 0.1, 1, 1)
drawer = turtle.Turtle()  # Turtle drawer
mutation_alphabet = 'F+-'  # Alphabet for mutation
generation_number = 100  # Number of generations for the test
population_size = 50  # Population of one generation
rule_iterations = 3  # Number of rule iteration. The complexity of species grown exponentially, be careful with high values
generation_gap = 0.2 # Proportion of species in generation replaced by new ones

# Line segment intersection algorithm by Bryce Boe
# More info: http://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


# Line segment intersection algorithm by Bryce Boe
# More info: http://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


# Execution process for chromosome
# Sends commands to Turtle drawer
# Returns 2-tuple with vertices and edges of generated species
def execute_chromosome(chromosome):
    positions_stack = []
    vertices = [drawer.pos()]
    edges = []
    for symbol in chromosome:
        if (symbol == '['):
            positions_stack.append((drawer.pos(), drawer.heading()))
        elif (symbol == ']'):
            position = positions_stack.pop()
            drawer.setpos(position[0])
            drawer.setheading(position[1])
        elif (symbol == 'F'):
            old_position = drawer.pos()
            drawer.penup()
            drawer.forward(drawer_step)
            drawer.pendown()
            vertices.append(drawer.pos())
            edges.append((old_position, drawer.pos()))
        elif (symbol == 'f'):  # Defined but not used in the original paper
            drawer.forward(drawer_step)
        elif (symbol == '+'):
            drawer.right(drawer_angle)
        elif (symbol == '-'):
            drawer.left(drawer_angle)
    return (vertices, edges)


# Check the chromosome or rule for correctness (square braces should be well-balanced)
def chromosome_is_correct(chromosome):
    stack_depth = 0
    for symbol in chromosome:
        if (symbol == '['):
            stack_depth += 1
        if (symbol == ']'):
            stack_depth -= 1
            if (stack_depth < 0):
                return False
    return stack_depth == 0


# Apply rule for chromosome (simply replace each 'F' by the rule pattern
def apply_rule(rule, chromosome):
    new_chromosome = ''
    for symbol in chromosome:
        if (symbol == 'F'):
            new_chromosome += rule
        else:
            new_chromosome += symbol
    return new_chromosome


# Replace random selected element by the sequence of random generated commands
# Returns given rule if mutation was unsuccessful
def rule_symbol_mutation(rule):
    # Select random position for mutation, avoid edges of blocks
    mutation_position = random.randint(0, len(rule) - 1)
    while (rule[mutation_position] == '[' or rule[mutation_position] == ']'):
        mutation_position = random.randint(0, len(rule) - 1)

    # Generate random sequence of commands, so-called mutation
    mutation_length = random.randint(0, 5)
    mutation_chromosome = ''
    for index in range(0, mutation_length):
        mutation_chromosome += mutation_alphabet[random.randint(0, len(mutation_alphabet) - 1)]

    # Generate new rule
    if (random.random() < 0.1):  # Add new branching(block) into rule
        new_rule = rule[:mutation_position] + '[' + mutation_chromosome + ']' + rule[mutation_position + 1:]
    else:
        new_rule = rule[:mutation_position] + mutation_chromosome + rule[mutation_position + 1:]
    if (chromosome_is_correct(new_rule)):  # Check new rule
        return new_rule
    else:
        return rule


# Replace all commands in one random selected block by the sequence of random generated commands
# Returns given rule if mutation was unsuccessful
def rule_block_mutation(rule):
    # Search for all blocks in rule
    blocks_position = []
    for index in range(len(rule)):
        if (rule[index] == '['):
            blocks_position.append(index + 1)

    if len(blocks_position) <= 1:
        return rule

    # Randomly select one
    mutation_position = blocks_position[random.randint(0, len(blocks_position) - 1)]

    # Generate random sequence of commands, so-called mutation
    mutation_length = random.randint(0, 5)
    mutation_chromosome = ''
    for index in range(0, mutation_length):
        mutation_chromosome += mutation_alphabet[random.randint(0, len(mutation_alphabet) - 1)]

    # Search for block end
    stack_depth = 0
    block_end = 0
    for index in range(mutation_position, len(rule)):
        if (rule[index] == ']'):
            stack_depth -= 1
            if (stack_depth < 0):
                block_end = index
                break
        elif (rule[index] == '['):
            stack_depth += 1

    # Generate new rule and check it's correctness
    new_rule = rule[:mutation_position] + mutation_chromosome + rule[block_end:]
    if (chromosome_is_correct(new_rule)):
        return new_rule
    else:
        return rule


# Swap random selected blocks between two rules
# Returns given rules if crossover was unsuccessful
def rules_crossover(ruleL, ruleR):
    # Search for all blocks
    blocks_positionL = []
    blocks_positionR = []
    for index in range(len(ruleL)):
        if (ruleL[index] == '['):
            blocks_positionL.append(index + 1)

    for index in range(len(ruleR)):
        if (ruleR[index] == '['):
            blocks_positionR.append(index + 1)

    if len(blocks_positionL) <= 1 or len(blocks_positionR) <= 1 :
        return (ruleL, ruleR)

    # Select random blocks
    crossover_positionL = blocks_positionL[random.randint(0, len(blocks_positionL) - 1)]
    crossover_positionR = blocks_positionR[random.randint(0, len(blocks_positionR) - 1)]

    # Find end of the blocks
    block_endL = 0
    block_endR = 0

    stack_depth = 0
    for index in range(crossover_positionL, len(ruleL)):
        if (ruleL[index] == ']'):
            stack_depth -= 1
            if (stack_depth < 0):
                block_endL = index
                break
        elif (ruleL[index] == '['):
            stack_depth += 1
    stack_depth = 0
    for index in range(crossover_positionR, len(ruleR)):
        if (ruleR[index] == ']'):
            stack_depth -= 1
            if (stack_depth < 0):
                block_endR = index
                break
        elif (ruleR[index] == '['):
            stack_depth += 1

    # Generate new rules
    new_ruleL = ruleL[:crossover_positionL] + ruleR[crossover_positionR:block_endR] + ruleL[block_endL:]
    new_ruleR = ruleR[:crossover_positionR] + ruleL[crossover_positionL:block_endL] + ruleR[block_endR:]
    if (chromosome_is_correct(new_ruleL) and chromosome_is_correct(new_ruleR)):  # Check for correctness
        return (new_ruleL, new_ruleR)
    else:
        return (ruleL, ruleR)


# Calculates fitness function of the species based on following criteria:
# a) Positive phototropism
# b) Bilateral Symmetry
# c) Light gathering ability
# d) Structural stability
# e) Proportion of branching points
def fitness_function(vertices, edges):
    edges = set(edges)
    max_y = 0.0
    left_side = 0.0
    right_side = 0.0
    for vertex in vertices:
        if (vertex[1] < 0):
            left_side += abs(vertex[1])
        if (vertex[1] > 0):
            right_side += abs(vertex[1])
        if (vertex[0] > max_y):
            max_y = vertex[0]

    started_at = {}  # For each point, the number of edges ended at the point
    ended_at = {}  # For each point, the number of edges started at the point
    for edge in edges:
        if edge[0] not in started_at:
            started_at[edge[0]] = 1
        else:
            started_at[edge[0]] += 1
        if edge[1] not in ended_at:
            ended_at[edge[1]] = 1
        else:
            ended_at[edge[1]] += 1

    leaves = []
    for key, value in ended_at.items():
        if (value == 1):
            leaves.append(key)

    open_leaves = 0
    for leave in leaves:
        ray = turtle.Vec2D(100000000, leave[1])
        is_open = True
        for edge in edges:
            if intersect(leave, ray, edge[0], edge[1]):
                is_open = False
                break
        open_leaves += 1 if is_open else 0

    branch_starts = []
    mean_branches_count = 0
    for key, value in started_at.items():
        mean_branches_count += value
        if (value > 1):
            branch_starts.append(key)

    mean_branches_count = mean_branches_count / len(started_at)

    a = max_y
    if right_side == 0:
        right_side = 0.000001  # Some small value to avoid division by zero
    if (right_side == 0 or left_side / right_side == 0):
        b = 0
    else:
        b = 1 / (left_side / right_side)
    c = open_leaves
    d = 1.0 / mean_branches_count
    e = len(branch_starts) / len(edges)
    return (a * w[0] + b * w[1] + c * w[2] + d * w[3] + e * w[4]) / (w[0] + w[1] + w[2] + w[3] + w[4])

def process_species(rule):
    chromosome = 'F'  # Axiom for the D0L-System
    drawer.home()
    drawer.clear()
    for j in range(rule_iterations):  # Multiple rule application
        chromosome = apply_rule(rule, chromosome)
    (vertices, edges) = execute_chromosome(chromosome)  # Chromosome execution
    fitness = fitness_function(vertices, edges)  # Evaluating the species
    turtle.update()
    return fitness

def __main__():
    # Configure Turtle drawer to disable drawing animations
    turtle.tracer(0, 0)
    drawer.hideturtle()
    # Basic rule was selected from the original paper
    basic_rule = 'F[+F]+[+F-F-F]-F[-F][-F-F]'
    current_rules = []
    for index in range(population_size):
        current_rules.append(basic_rule)
    # current_rules = (basic_rule, basic_rule)

    def compare(item1, item2):
        if item1[0] < item2[0]:
            return -1
        elif item1[0] > item2[0]:
            return +1
        else:
            return 0

    for i in range(0, generation_number):  # Generate configured number of generation
        species_list = []
        for index in range(len(current_rules)):
            fitness = process_species(current_rules[index])
            species_list.append((fitness, current_rules[index]))
        species_list = sorted(species_list, key = lambda tuple: tuple[0], reverse = False)
        best_species = species_list[len(species_list) - 1][1]
        for index in range(int(len(species_list) * generation_gap)):
            action_prob = random.random()  # Randomly select action among two types of mutations and crossover
            if action_prob <= 1 / 3:
                new_species = rule_symbol_mutation(best_species)
                fitness = process_species(new_species)
                species_list[index] = (fitness, new_species)
            elif action_prob <= 2 / 3:
                new_species = rule_block_mutation(best_species)
                fitness = process_species(new_species)
                species_list[index] = (fitness, new_species)
            else:
                new_species = rules_crossover(best_species, species_list[len(species_list) - 2][1])
                fitness1 = process_species(new_species[0])
                fitness2 = process_species(new_species[1])
                species_list[index] = (fitness1, new_species[0])
                species_list[index + 1] = (fitness2, new_species[1])
                index += 1

        current_rules = []
        for index in range(len(species_list)):
            current_rules.append(species_list[index][1])
        # Visualise the best species
        process_species(best_species)
        turtle.update()

    print("Generation completed!")
    turtle.mainloop()


__main__()
