import pandas as pd
from Event import Event
from Team import Team
from Constant import Constant
import json

class Game:
    def __init__(self, path_to_json, event_index, analytics=''):
        self.home_team = None
        self.guest_team = None
        self.event = None
        self.path_to_json = path_to_json
        self.analytics=analytics
        with open(self.path_to_json) as f:
            self.events={int(x['eventId']): x for x in json.load(f)['events']}
        if(event_index==-1):
            self.play_full()
        else:
            self.set_event(event_index)

    def set_event(self, index):
        event=self.events[index]
        self.event = Event(event, self.analytics)
        self.home_team = Team(event['home']['teamid'])
        self.guest_team = Team(event['visitor']['teamid'])

    def play_full(self):
        event=self.events[list(self.events.keys())[0]]
        moments={}
        for k, e in self.events.items():
            for m in e['moments']:
                moments[m[1]]=m
        event['moments']=[v for k, v in moments.items()]
        self.event=Event(event, self.analytics)

    def start(self):
        self.event.show()
