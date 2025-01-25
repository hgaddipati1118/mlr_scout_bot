class Player:
    def __init__(self, playerID, playerName, Team, batType, pitchType, pitchBonus, hand,
                 priPos, secPos, tertPos, redditName, discordName, discordID, status, posValue):
        self.playerID = playerID
        self.playerName = playerName
        self.Team = Team
        self.batType = batType
        self.pitchType = pitchType
        self.pitchBonus = pitchBonus
        self.hand = hand
        self.priPos = priPos
        self.secPos = secPos
        self.tertPos = tertPos
        self.redditName = redditName
        self.discordName = discordName
        self.discordID = discordID
        self.status = status
        self.posValue = posValue

class PlateAppearance:
    def __init__(self, paID, league, season, session, gameID, inning, inningID, playNumber, outs, obc,
                 awayScore, homeScore, pitcherTeam, pitcherName, pitcherID, hitterTeam, hitterName, hitterID,
                 pitch, swing, diff, exactResult, oldResult, resultAtNeutral, resultAllNeutral, rbi, run,
                 batterWPA, pitcherWPA, pr3B, pr2B, pr1B, prAB):
        self.paID = paID
        self.league = league
        self.season = season
        self.session = session
        self.gameID = gameID
        self.inning = inning
        self.inningID = inningID
        self.playNumber = playNumber
        self.outs = outs
        self.obc = obc
        self.awayScore = awayScore
        self.homeScore = homeScore
        self.pitcherTeam = pitcherTeam
        self.pitcherName = pitcherName
        self.pitcherID = pitcherID
        self.hitterTeam = hitterTeam
        self.hitterName = hitterName
        self.hitterID = hitterID
        self.pitch = pitch
        self.swing = swing
        self.diff = diff
        self.exactResult = exactResult
        self.oldResult = oldResult
        self.resultAtNeutral = resultAtNeutral
        self.resultAllNeutral = resultAllNeutral
        self.rbi = rbi
        self.run = run
        self.batterWPA = batterWPA
        self.pitcherWPA = pitcherWPA
        self.pr3B = pr3B
        self.pr2B = pr2B
        self.pr1B = pr1B
        self.prAB = prAB
