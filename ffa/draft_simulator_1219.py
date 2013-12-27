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
import random
import matplotlib.pyplot as plt

#===============================================================================
# My Class
#===============================================================================
class DraftSimulator:

    def __init__(self, playerInfo, teamsDraft):

        # Save Info Passed to Object
        self.playerInfo = playerInfo;
        self.teamStrategy = teamsDraft;

        self.SetInstanceVariables()

    def SetInstanceVariables(self):
        print 'Creating Draft Simulator Class!';

        # Set Constant Terms
        self.DRAFTS_TO_RUN          = 100;
        self.PRINT_DRAFT_RESULTS    = True;
        self.PRINT_PLAYER_ANALYSIS  = True;
        self.PRINT_PLOTS            = False;
        
        self.teamNames      = self.teamStrategy.index;
        self.numOfTeams     = len(self.teamNames);
        self.rounds         = sum(self.playerInfo.ix['spots']);
        
        # Static
        self.SelectType     = 'max_points';
        self.BreakTieType   = 'random';
        self.DF_TEAM_COLUMN        = ['pick', 'pos', 'pts', 'id'];     # output format
                                                                
    def CreateTeams(self):
        
        '''Create a Dictionary and convert to a panel'''
        
        # ToDo: Should this be moved? (maybe not since it clears teams?)
        
        # Set Local Variables
        teamsTmp        = {};       

        # Create Panel - Loop thru each team name and generate Data Frame
        for name in self.teamNames:
            teamFrame       = pd.DataFrame(columns=self.DF_TEAM_COLUMN,\
                              index=np.arange(self.rounds));
            teamsTmp[name]  = teamFrame;

        # Convert Dict to Panel
        self.teams   = pd.Panel(teamsTmp);
    
    def GenerateDraftOrder(self):
        
        # Set Variables
        self.DraftOrder = [];                       # Clear Draft Order Array
        namesTmp        = list(self.teamNames[:]);  # Reverse a local copy

        # Loop thru rounds, reversing team names to create snake draft
        for i in np.arange(self.rounds):
            self.DraftOrder.extend(namesTmp);
            namesTmp.reverse();
    
    def CreateDraftResultStruct(self):
        
        '''Store Results from Drafts'''
                
        colDraftRes = ['RND', 'TEAM', 'ID', 'POS', 'PTS'];
        idxDraftRes = np.arange(np.size(self.DraftOrder))
        
        self.DraftResults = pd.DataFrame(columns=colDraftRes, index=idxDraftRes);
        
    def GetAvailablePlayers(self, players, team):

        playersAv   = players.copy();
        posCnt      = team['pos'].value_counts();               

        # remove players that have reached limit
        for pos in posCnt.index:
            if posCnt[pos] >= self.playerInfo[pos]['spots']:
                playersAv = playersAv[playersAv.pos != pos];    

        return(playersAv);

    def RemovePlayersOnTeam(self, players, team):

        for key in team['id']:
            players = players[players['id'] != key];
            print key

        return(players);

    def SelectPlayer(self, players, teamPick):
 
        # -----------------------------------------------------------
        # Returns the index (select) of the player to select
        #   - Choose how to select a player (max points, slope, pos)
        #   - Choose how to break a tie
        #   - This is one of the most important functions!
        # -----------------------------------------------------------
        draft       = self.teamStrategy.ix[teamPick]
        playersAv   = self.GetAvailablePlayers(players, self.teams[teamPick]);
        
        # Select Player based on method
        if draft['strategy']  == 'max_points':
            options     = playersAv.pts == playersAv.pts.max();

        elif draft['strategy']  == 'depth_search':
            options     = self.DepthFirstSearch(teamPick, playersAv);

        elif draft['strategy']  == 'user':
            options  = self.SelectPlayerManually(playersAv, draft.name);
            
        else:
            print 'Draft Selection Type not Supported yet!'

        # Method to break tie (multi-player selection)
        if draft['breakTie'] == 'random':
            select  = random.choice(options[options==True].index);

        elif draft['breakTie'] == 'first':
            select  = options[options==True].index[0];

        elif draft['breakTie'] == 'last':
            select  = options[options==True].index[-1];
            
        else:
            print 'Break Tie Type not Supported yet!'
 
        return(select);
        
    def SelectPlayerManually(self, players, name):
        
        turns       = 0;
        MAX_TURNS   = 5;
        
        print 'Your Team:\n', self.teams[name];
        print '\nAvailable Players:\n', players;
        
        while turns < MAX_TURNS:
            
            # check if there is only one player left
            if players.shape[0] == 1:
                select = players.index[0];
                print '\nYour last pick was:\n', players;
                break;
            
            # Ask user to select player
            while True:
                turns   += 1;
                try:
                    select  = np.int64(raw_input('\nYo ' + name + ' Select a Player (use LHS index to select):\n'));
                    break;
                except ValueError:
                    print "\nOops!  That was not a valid number.\nPlease try (again) to Select a Player:";
                    
            # Check that user selected a valid player
            check   = players[players.index == select]    
            if check.empty:
                print '\nNo player with index = ' + str(select) + ', Please Select Again!';
            else:
                break;
                
        # Proceed to draft-max-player valid player never selected
        if turns == MAX_TURNS:
            print 'Okay, someone does not know how to draft!';
            print 'Do not worry, I will choose the player with the max projected points for you!';
            options     = players.pts == players.pts.max();
        else:
            options     = players.id == players.ix[select]['id'];
            
        return(options);
            
    def DepthFirstSearch(self, teamPick, players):
        
        # Create lists (yes not numpy arrays)
        rnd     = [];
        pos     = [];
        team    = self.teams[teamPick];

        if team.pos.last_valid_index() == None:
            CURRENT_ROUND   = 0;
        else:
            CURRENT_ROUND   = team.last_valid_index() + 1;
        
        rnd.append(CURRENT_ROUND);
        
        # Create lists of data frames
        playersOpt  = [];playersOpt.append(players.copy()); 
        optionsTmp  = [];optionsTmp.append(team.copy());
        optionsCmp  = list(optionsTmp); # make a new copy
        optionsCmp.pop(0);              # Empty Panel - no completed teams yet!
        
        self.DepthFirstSearchRecur(teamPick, pos, rnd, playersOpt, optionsTmp, optionsCmp)
        
        # Find player to draft based on max points:
        # ToDo: If branches tie need to return options that reflect this!
        maxPts      = 0;
        PLAYER_ID   = optionsCmp[0].id[0];
        
        for df in optionsCmp:
            pts = df.pts.sum();
            if pts > maxPts:
                maxPts      = pts;
                PLAYER_ID   = df.id[CURRENT_ROUND];
                
        options     = players.id == PLAYER_ID;
        
        return(options)
               
    def DepthFirstSearchRecur(self, teamPick, pos, rnd, playersOpt, optionsTmp, optionsCmp):        
 
        # Get all branches for current node
        team        = optionsTmp[0];
        
        if pos != []:       # Skip on first time around
            # For first branch - Draft and add player to team:       
            playersAv       = playersOpt[0][playersOpt[0]['pos'] == pos[0].pop(0)] 
            options         = playersAv.pts == playersAv.pts.max();
            select          = random.choice(options[options==True].index);
            playersOpt[0]   = playersOpt[0].drop(select);
            self.PlacePlayerOnTeam(playersAv.ix[select], optionsTmp[0], rnd[0], -2);
            #playersOpt[0]   = self.DropProjectedPlayers(rnd[0], playersOpt[0], teamPick);
            pos.pop(0) if pos[0] == [] else 0;
            rnd[0]          += 1;
            
        # After selection update available players
        playersOpt[0]   = self.GetAvailablePlayers(playersOpt[0], team);
        posAv           = playersOpt[0].pos.unique();
         
        
        # Save rest of branches
        if posAv.any():
            pos.insert(0, posAv.tolist());
            
        for i in posAv[1:]:
            rnd.insert(0,rnd[0]);
            optionsTmp.insert(0, team.copy());
            playersOpt.insert(0, playersOpt[0].copy());
 
        # check if current branch has been exhausted
        if rnd[0] == self.rounds:
            print len(optionsCmp)
            rnd.pop(0);
            playersOpt.pop(0);
            optionsCmp.insert(0, optionsTmp.pop(0));
            #print optionsTmp
            #print optionsCmp
            
        # If all nodes + branches have not been expanded
        if pos != []:
            self.DepthFirstSearchRecur(teamPick, pos, rnd, playersOpt, optionsTmp, optionsCmp)
            
    def DropProjectedPlayers(self, rnd, players, teamName):
        
        # For Breath First Search Algo
        # Note: Must have already dropped players on team from players!

        # Get the number of rounds completed
        numDropPlayers = -1;
        teamDraftCount = 0;

        for turn in self.DraftOrder:
            #print 'turn = ', turn, 'rnd # = ', teamDraftCount, 'to drop =', numDropPlayers
            if turn == teamName:
                teamDraftCount += 1;
            if teamDraftCount > rnd + 1:
                break;
            if teamDraftCount > rnd:
                numDropPlayers += 1;
        
        # Drop projected-to-be-gone-players
        playersLeft = players[numDropPlayers:].copy();

        # Re-Add player by positon if all have been removed
        for pos in players.pos.unique():
            if not playersLeft.pos[playersLeft.pos == pos].any():
                
                # Find Min Player for Pos
                playerOpt   = players[players.pos == pos]
                options     = playerOpt.pts.min() == playerOpt.pts
                select      = random.choice(options[options==True].index);
                
                playersLeft = playersLeft.append(players.ix[select]);
                playersLeft.sort(columns='pts', ascending=False, inplace=True);

            
        return(playersLeft);
    
    def PlacePlayerOnTeam(self, player, team, rnd, i):
        
        # Add Player to Team
        team.ix[rnd]['pts']     = player['pts'];
        team.ix[rnd]['pos']     = player['pos'];
        team.ix[rnd]['id']      = player['id'];
        team.ix[rnd]['pick']    = i+1;

    def AddPlayerToDraftResults(self, player, i, teamName):

        rnd         = np.uint(i/self.numOfTeams);
        
        self.DraftResults.ix[i]['TEAM']  = teamName;
        self.DraftResults.ix[i]['RND']   = rnd + 1;
        self.DraftResults.ix[i]['ID']    = player['id'];
        self.DraftResults.ix[i]['POS']   = player['pos'];
        self.DraftResults.ix[i]['PTS']   = player['pts'];
        
    def RunDraft(self, playersNew):

        # Draft Initial Conditions:
        self.CreateTeams();
        self.GenerateDraftOrder();
        self.CreateDraftResultStruct();
        
        # Create Local Copies        
        #teams       = self.teams;        # DEL: Why is this necessary
        players     = playersNew.copy();

        # Kick of Draft
        for i, teamPick in enumerate(self.DraftOrder):

            team        = self.teams[teamPick];             # ToDo: MESSY TOO!
            rnd         = np.uint(i/self.numOfTeams);       # ToDo: Remove and self calculate
            
            select      = self.SelectPlayer(players, teamPick);
            self.PlacePlayerOnTeam(players.ix[select], team, rnd, i);
            self.AddPlayerToDraftResults(players.ix[select], i, teamPick);
            players     = players.drop(select);
            
        # Draft Complete!
        if self.PRINT_DRAFT_RESULTS == True and self.DRAFTS_TO_RUN < 5:
            print '\nDraft Results:\n', self.DraftResults;    
        
    def RunMultipleDrafts(self, players):
        
        '''Use to get statistical information from running multiple drafts'''
        
        # Create Empty Data Frames to save multi-run data
        playersAnalysis  = pd.DataFrame(index=players['id'].values, columns=['win', 'los', 'avg']).fillna(0);
        teamsAnalysis    = pd.DataFrame(index=self.teamNames,       columns=['win', 'los', 'avgPts', 'rnk']).fillna(0);

        # Run-Multi Drafts and Gather Data
        # -----------------------------------------------------------
        print '\nDraft Simulation in progress!\nPlease be patient... Great Minds are at Work...\n',;
        
        for i in np.arange(self.DRAFTS_TO_RUN):

            # Kick off Draft
            self.RunDraft(players);
            
            # Grab team points from draft
            points      = self.teams.ix[:,:,'pts'];
            summary     = points.sum().order(ascending=False);
            rnkSum      = summary.rank(ascending=False);
            
            # Team Performance - Running Sum
            teamsAnalysis['win'][rnkSum.index[ 0]] += 1;
            teamsAnalysis['los'][rnkSum.index[-1]] += 1;
            teamsAnalysis['avgPts'] += summary;
            teamsAnalysis['rnk']    += rnkSum;
            
            # Player Performance - Running Sum
            playersAnalysis['win'][self.teams[rnkSum.index[ 0]]['id']] += 1;
            playersAnalysis['los'][self.teams[rnkSum.index[-1]]['id']] += 1;
            for name in self.teams: # Player Rank - Running Sum
                playersAnalysis['avg'][self.teams[name]['id']] += rnkSum[name];
                
        # Analyze Data
        self.AnalyzeDraftResults(playersAnalysis, teamsAnalysis);
        print 'Close figure to return'
        plt.show();
        
        return(playersAnalysis);

    def AnalyzeDraftResults(self, playersAnalysis, teamsAnalysis):
        
        GOOD_WIN_CHANCE   = 2 * 100 / self.numOfTeams;      # twice the average chance of winning
        MIN_RUNS_TO_PRINT = self.DRAFTS_TO_RUN > 4;
        
        # Average Multi-run Data
        playersAnalysis['win']  = np.float16( playersAnalysis['win'] * 100 / self.DRAFTS_TO_RUN );
        playersAnalysis['los']  = np.float16( playersAnalysis['los'] * 100 / self.DRAFTS_TO_RUN );
        playersAnalysis['avg']  = np.float16( playersAnalysis['avg'] * 100 / self.DRAFTS_TO_RUN ) / 100;

        teamsAnalysis['rnk']    = np.float16( teamsAnalysis['rnk']) / self.DRAFTS_TO_RUN;
        teamsAnalysis['avgPts'] = np.float64( teamsAnalysis['avgPts']) / self.DRAFTS_TO_RUN;

        # Print Analysis:
        print '\nLet\'s analyze some stats from the draft:';
        print teamsAnalysis.sort(columns='rnk', ascending=True); 
 
        if self.PRINT_PLAYER_ANALYSIS == True and MIN_RUNS_TO_PRINT:
            print '\nWin + Lose odds vs. player:';
            print playersAnalysis.sort(columns='avg');
 
        if self.PRINT_PLOTS == True and MIN_RUNS_TO_PRINT:          
            if playersAnalysis[playersAnalysis > GOOD_WIN_CHANCE].dropna(how='all').empty:
                print 'Looks like no one has a strong statistical chance of winning...';
                playersAnalysis.plot(kind='bar', stacked=True);
            else:
                playersAnalysis[playersAnalysis > GOOD_WIN_CHANCE].dropna(how='all').plot(kind='bar', stacked=True);
                pass;
                    

        # DEL: Save to class: (can remove this...)
        self.pData = playersAnalysis;
        self.tData = teamsAnalysis;
        