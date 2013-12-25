'''
Created on Dec 12, 2013

@author: rpatel

################################################################################
#                                                                              #
# Author:   Rishi Patel                                                        #
# Date:     2013.08.10                                                         #
#                                                                              #
# Purpose:  Generic Class used Analyze Football Stats                          #
#                                                                              #
# ToDo:                                                                        #
#   1. Break this class up (too much happening!)                               #
#       - Need moduler structure                                               #
#   2. Target Structure:                                                       #
#       - Class: Read Data & Convert to Generic Format (munge)                 #
#           - ToDo: Convert columns to generic format                          #
#           - ToDo: Pass a dictionary linking the current to generic           #
#       - Class: Fantasy Analysis                                              #
#           - Compute points and stats based on points                         #
#           - Algorithms for ranking by position and overall                   #
#               - Consider: variance, injury, age                              #
#           - Make projections, player-by-player analysis                      #
#           - Home, turf, travel, strength of defense/offense                  #
#                                                                              #
################################################################################

'''

#===============================================================================
# Load Modulues
#===============================================================================
import pandas as pd
import numpy as np

#===============================================================================
# My Class
#===============================================================================
class CreatePlayers:

    def __init__(self, playerInfo, numOfTeams):
        
        # Save Info Passed to Object
        self.playerInfo     = playerInfo;
        self.numOfTeams     = numOfTeams;

        self.SetInstanceVariables();
        self.CreatePlayerFrame();
        self.GeneratePlayersByEquation();
        
    def SetInstanceVariables(self):

        print 'Initializing Player Data Frame!';
        
        # Set Const Terms:
        self.EquationType   = 'linear';
        self.pColumns       = ['rnk', 'pts', 'pos', 'id', 'posRnk'];     # output format

    def CreatePlayerFrame(self):

        # Maybe just dump this in 'Set Instance Variables'
        self.numOfPlayers   = self.numOfTeams * sum(self.playerInfo.ix['spots']);
        self.players        = pd.DataFrame(columns=self.pColumns, \
                              index=np.arange(self.numOfPlayers));
        self.players.index.name = 'idx'
        
    def GeneratePlayersByEquation(self):
        
        playerIdx   = 0;    # index for filling in each row of player frame

        # Get an array of points by each position
        for i, pos in enumerate(self.playerInfo.columns):
            
            playersPtsPos   = self.GetPointsByPos(pos);

            # Fill in array of points one-by-one
            for j, pts in enumerate(playersPtsPos):
                id = pos+str(j+1);
                self.players.ix[playerIdx]  = ['na', pts, pos, id, id];
                playerIdx   += 1;

        # RANK BY POINTS: Below order is VERY IMPORTANT!!!
        self.players.sort(columns='pts',ascending=False,inplace=True);
        self.players['rnk']     = np.arange(self.players.pts.count()) +1
        
    def GetPointsByPos(self, pos):

        playerPosRng    = np.arange(self.numOfTeams * self.playerInfo[pos]['spots']);

        if self.EquationType == 'linear':
            points  = self.playerInfo[pos]['start'] - \
                      playerPosRng * self.playerInfo[pos]['slope'];
        
        elif self.EquationType == 'exp_decay':
            print 'ToDo: Add exp decay function...';
        
        else:
            print 'Warning: No Equation Type Recognized!';
            points  = self.playerInfo[pos]['start'] - playerPosRng * 0;
        
        return(points);
