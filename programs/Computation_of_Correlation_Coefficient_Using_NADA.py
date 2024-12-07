from nada_dsl import *

def nada_main():
    """
    This program computes the squared correlation coefficient between two vectors, 
    where the vectors are provided by two parties (P0 and P1). 

    Party 0 provides 10 points (x_i, y_i), and Party 1 provides 10 points (x_j, y_j).
    """

    # Define constants
    nr_parties = 2
    p0_points = 10  # Number of points provided by Party 0
    p1_points = 10  # Number of points provided by Party 1
    precision = 5  # Precision for the final correlation coefficient
    total_points = p0_points + p1_points  # Total number of points

    # Create parties
    parties = [Party(name=f"Party{i}") for i in range(nr_parties)]
    outparty = Party(name="OutParty")

    # Initialize vectors for x and y values
    xi_vector = []
    yi_vector = []

    # Input from Party 0
    for i in range(p0_points):
        xi_vector.append(SecretInteger(Input(name=f"x{i}", party=parties[0])))
        yi_vector.append(SecretInteger(Input(name=f"y{i}", party=parties[0])))

    # Input from Party 1
    for i in range(p1_points):
        xi_vector.append(SecretInteger(Input(name=f"x{i + p0_points}", party=parties[1])))
        yi_vector.append(SecretInteger(Input(name=f"y{i + p0_points}", party=parties[1])))

    # Compute necessary summations
    sum_x = xi_vector[0]
    sum_y = yi_vector[0]
    sum_xy = xi_vector[0] * yi_vector[0]
    sum_xx = xi_vector[0] * xi_vector[0]
    sum_yy = yi_vector[0] * yi_vector[0]

    # Calculate the sums for the entire dataset
    for i in range(1, total_points):
        sum_x += xi_vector[i]
        sum_y += yi_vector[i]
        sum_xy += xi_vector[i] * yi_vector[i]
        sum_xx += xi_vector[i] * xi_vector[i]
        sum_yy += yi_vector[i] * yi_vector[i]

    # Define the formula for squared correlation coefficient (r_xy)^2:
    # (n * sum_xy - sum_x * sum_y)
    # --------------------------------------------
    # (n * sum_xx - sum_x * sum_x) * (n * sum_yy - sum_y * sum_y)
    n = Integer(total_points)  # Total number of data points
    n_times_sum_xy = n * sum_xy
    sum_x_times_sum_y = sum_x * sum_y
    left_denominator = n * sum_xx - sum_x * sum_x
    right_denominator = n * sum_yy - sum_y * sum_y

    numerator = n_times_sum_xy - sum_x_times_sum_y
    denominator = left_denominator * right_denominator

    # Square the numerator and compute the final correlation coefficient squared
    squared_numerator = numerator * numerator * Integer(10 ** precision)
    r_squared = squared_numerator / denominator

    # Determine the sign of the correlation coefficient
    sign = n_times_sum_xy > sum_x_times_sum_y

    # Return the results
    return [
        Output(r_squared, "correlation_coefficient_squared", outparty),
        Output(sign, "sign", outparty)
    ]