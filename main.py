from Game import Game
import argparse

parser = argparse.ArgumentParser(description='Process arguments about an NBA game.')
parser.add_argument('--path', type=str, default='0021500495.json',
                    help='a path to json file to read the events from')
parser.add_argument('--event', type=int, default=0,
                    help="""an index of the event to create the animation to
                            (the indexing start with zero, if you index goes beyond out
                            the total number of events (plays), it will show you the last
                            one of the game)""")
parser.add_argument('--analytics', type=str,
                    help="""View some analysis on the game""")

args = parser.parse_args()

game = Game(path_to_json=args.path, event_index=args.event, analytics=args.analytics)
game.start()
