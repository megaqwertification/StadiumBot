class EventRecord:
    def __init__(self, event_id=None, player=None, type='timed', score=None, sources=[], date=None, tas=False, emulator=True, tags=[], ver=None):
        '''
        Init with the default/expected values in the database schema
        '''
        self.event_id = event_id
        self.player = player
        self.type = type
        self.score = score
        self.sources = sources
        self.date = date
        self.tas = tas
        self.emulator = emulator
        self.tags = tags
        self.ver = ver