'''
Created on Dec 20, 2013

@author: rkpatel
'''
import pandas as pd;
import numpy as np;
import matplotlib.pyplot as plt;
import os.path;
    
def main():
    oP          = GetPlayers();
    oP.databaseDir    = r'../../../Database/Football/PlayerStatsByYearPFB'
    players2    = oP.GetSeasonStats(2012)
    playersNew  = oP.CleanPlayersForDraftSim(players2);
        
    print 'Done Debug Marker'
    
class GetPlayers:
    
    def __init__(self):
        self.SetInstanceVariables()

    def SetInstanceVariables(self):
        
        # Set Instance Variables
        print "Creating Analysis Class...\n"
        
        # Analysis Variables
        self.NumOfPlayers   = 30                    # Num of players to observe
        self.MinQualifyPts  = 50                   # Threahold to qualify player
        self.SaveFigureEn   = False                 # if = true > Save Plots
        
        self.MIN_PLAYERS_NEEDED     = 100
        
        # Fantasy Variables
        self.ptsData        = {'PassYds' : [0.025],  # Make 0.04 (1 pt/25yards)?
                               'PassTDs' : [5],     # = pts / TD
                               'PassInt' : [-2],    # = pts / INT
                               'RushYds' : [0.067],   # = pts / yard
                               'RushTDs' : [5],     # = pts / TD
                               'RecComp' : [0.25],   # = pts / comp
                               'RecYds'  : [0.05],   # = pts / yard
                               'RecTDs'  : [5]}     # = pts / TD
        
        self.FanPosition    = ['QB', 'RB', 'WR', 'TE']  # Used for classing players

        # Database Dependent Variables
        self.FileExt        = '_FantasyStats.csv'           # File Name Ext
        #self.databaseDir    = r'C:\Users\rpatel\Dropbox\Database\Football\ProFootBallStats'
        self.databaseDir    = r'../../Database/Football/PlayerStatsByYearPFB'
        self.FigPath        = os.path.join(self.databaseDir,'Analysis\\')
        self.RemoveCol      = ['Rk', 'VBD']
        self.StandardCol    = ['Name', 'Team', 'Age', 'GP', 'GS', 'PassCmp', 'PassAtt', 
                               'PassYds', 'PassTDs', 'PassInt', 'RushAtt', 'RushYds', 
                               'RushAvg', 'RushTDs', 'RecComp', 'RecYds', 'RecAvg', 'RecTDs', 
                               'Position', 'FantTotalPts', 'FantPosRank', 'FantOvrRank']
        
    def GetSeasonStats(self, year):
        
        # Get Data from DataBase > Clean Up > Get Fantasy Points > Plot/Analysis

        FilePath    = os.path.join(self.databaseDir, str(year) + self.FileExt)
        self.df     = pd.read_csv(FilePath)

        self.CleanUpData()
        self.ComputeFantasyPoints()
        self.df.FileName = year             # TODO: Should move but breaks
        
        return(self.df.copy());
    
    def CleanUpData(self):
        
        ''' Clean up Data to match Draft Simulator Class format '''

        self.df         = self.df.fillna(0)
        self.df         = self.df.drop(self.RemoveCol, axis=1)
        self.df.columns = self.StandardCol
        
    def ComputeFantasyPoints(self):
        
        # Generate Fantasy Points based on available data and League Settings

        pts     = np.zeros_like(self.df['PassYds'])     # Create a list of zeros
        
        # Loop and Compute Fantasy Points for each Category
        for name in self.ptsData.keys():
            curPts  = self.ptsData[name] * self.df[name]
            pts     = curPts + pts
            
            self.df[name + 'FantPts'] = curPts
    
        # Add Point Total to Data Frame
        # ToDo: avoid reassigning...
        self.df.FantTotalPts = pts
        self.df     = self.df[self.df.FantTotalPts > self.MinQualifyPts]
        self.df     = self.df.sort(columns='FantTotalPts',ascending=False) 
        self.df     = self.df.set_index(self.df.Name)

    def CleanPlayersForDraftSim(self, players):
        
        indexNew    = players.index;
        columnsNew  = ['rnk', 'pts', 'pos', 'posRnk'];     # output format
        columnsOld  = ['FantOvrRank', 'FantTotalPts', 'Position', 'FantPosRank']
        playersNew  = pd.DataFrame(index=indexNew, columns=columnsNew)

        for i, col in enumerate(columnsNew):
            colOld              = columnsOld[i];
            playersNew[col]     = players[colOld];
 
        playersNew.posRnk   = playersNew.pos + playersNew.posRnk.map(int).map(str);
        playersNew['id']    = playersNew.index.map(str)
        playersNew          = playersNew[playersNew.rnk != 0]    # warning: how many people do we remove?
        playersNew.index    = playersNew.rnk;
        playersNew.index.name = 'idx'
        
        if playersNew.rnk.count() < self.MIN_PLAYERS_NEEDED:
            print 'WARNING: Critically low number of players = ', playersNew.rnk.count()
        
        playersNew.sort(columns='rnk', ascending=True, inplace=True);

        return(playersNew)
        
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        pass


if __name__ == "__main__":
    
    main();
    
    
    