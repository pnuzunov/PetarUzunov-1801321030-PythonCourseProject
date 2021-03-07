import ant_colony_simulator as acs
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file_input')
    args = parser.parse_args()

    if(args.file_input):
        acs.run(args.file_input)
    else:
        acs.run('./acs_input.json')

# input("Press any key to continue...")
