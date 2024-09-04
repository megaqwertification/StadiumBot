class BttRecord:
    def __init__(self, character=None, stage=None, player=None, score=None, sources=[], date=None, tas=False, emulator=True, debug=False, tags=[], ver=None):
        '''
        Init with the default/expected values in the database schema
        '''
        self.character = character
        self.stage = stage
        self.player = player
        self.score = score
        self.sources = sources
        self.date = date
        self.tas = tas
        self.emulator = emulator
        self.debug = debug
        self.tags = tags
        self.ver = ver