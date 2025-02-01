import random


def generate_powerball_numbers():
    # Generate 5 random Pick numbers in the range of 1 to 69
    pick_numbers = random.sample(range(1, 70), 5)

    # Generate a random Powerball number in the range of 1 to 26
    powerball_number = random.randint(1, 26)

    return sorted(pick_numbers), powerball_number


def main():
    pick_numbers, powerball_number = generate_powerball_numbers()

    print("Tonight's Powerball numbers are:")
    print("Pick Numbers:", pick_numbers)
    print("Powerball Number:", powerball_number)


if __name__ == "__main__":
    main()
