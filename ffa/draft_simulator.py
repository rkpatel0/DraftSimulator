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
import os
import markdown as md

#===============================================================================
# My Class
#===============================================================================
class DraftSimulator:

    def __init__(self, playerInfo, teamsDraft):

        # Save Info Passed to Object
        self.playerInfo     = playerInfo       # Master List of simPlayers
        self.teamStrategy   = teamsDraft       

        # Set Default Conditons
        self.SetDraftDefault()
        self.SetAnalsyisConditions()
        self.SetConstants()
        
    def SetDraftDefault(self):

        self.DRAFTS_TO_RUN      = 1
        self.RUNS_TO_LEARN      = 10
        self.SEARCH_DROP_RANK   = 'rnk'
        self.teamNames          = self.teamStrategy.index
        self.numOfTeams         = len(self.teamNames)
        self.rounds             = sum(self.playerInfo.ix['spots'])

    def SetAnalsyisConditions(self):
        
        self.PRINT_DRAFT_RESULTS    = True
        self.PRINT_PLAYER_ANALYSIS  = True
        self.PRINT_PLOTS            = True
        self.SAVE_DATA_PATH         = r'../../Analysis/'
        self.PROJECT_DIR            = 'TEST_ME/'
        
        self.PATH   = self.SAVE_DATA_PATH + self.PROJECT_DIR
        print 'Project Log Path:' + self.PATH
        
        if not os.path.exists(self.PATH):
            os.makedirs(self.PATH)
        
        self.LOG     = open(self.PATH + 'DraftResults.html', 'w');

    def SetConstants(self):
        self.DF_TEAM_COLUMN     = ['pick', 'pos',   'pts', 'posRnk', 'id']
        self.DF_DRAFTRES_COLUMN = ['RANK', 'P_IDX', 'RND', 'TEAM', 'ID', 'POS', 'PTS']
        self.LONG_STR           = '------------------------------------------------\n'
                        
    def CreateTeams(self):
        
        # Loop thru teamnames - Dict of Team Data Frame
        teamsTmp        = {}       

        for name in self.teamNames:
            teamFrame       = pd.DataFrame(columns=self.DF_TEAM_COLUMN, index=np.arange(self.rounds))
            teamFrame.name  = name          # ToDo: Cannot save data frame name to panel
            teamsTmp[name]  = teamFrame
            teamFrame.index.name = 'rnd'

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
 
        # Index for Draft Results (just 0:1:NUM_OF_PICKS)
        idxDraftRes = np.arange(np.size(self.DraftOrder))
        
        self.DraftResults = pd.DataFrame(columns=self.DF_DRAFTRES_COLUMN, index=idxDraftRes);
        self.DraftResults.index.name    = 'pick #'
        
    def GetAvailablePlayers(self, simPlayers, team):

        ''' Return available simPlayers to draft based on simPlayers/positions already drafted'''
        
        # Copy simPlayers - cannot alter total avaialbe simPlayers for all teams
        playersAv   = simPlayers.copy();
        teamPos = team['pos']
        
        # remove simPlayers that have reached limit
        for pos in self.playerInfo.columns:
            if teamPos[teamPos == pos].count() >= self.playerInfo[pos]['spots']:
                playersAv = playersAv[playersAv.pos != pos]

        return(playersAv);

    def SelectPlayer(self, simPlayers, teamPick):
 
        ''' Return the INDEX of player-to-draft'''
 
        playersAv   = self.GetAvailablePlayers(simPlayers, self.teams[teamPick])
        options     = self.GetTeamDraftOptions(playersAv, teamPick)
        select      = self.SelectBetweenDraftOptions(options, teamPick)
        
        return(select)
    
    def GetTeamDraftOptions(self, simPlayers, teamPick):
        
        ''' Find Draft Options Based on Team Draft Strategy '''
        
        draft   = self.teamStrategy.ix[teamPick]
        
        if draft['strategy']  == 'max':
            options     = simPlayers.pts == simPlayers.pts.max();
            
        elif draft['strategy']  == 'rank':
            options     = simPlayers.rnk == simPlayers.rnk.min();
            
        elif draft['strategy']  == 'user':
            options  = self.SelectPlayerManually(simPlayers, draft.name);

        elif draft['strategy']  == 'depth':
            options     = self.DepthFirstSearch(teamPick, simPlayers);

        elif draft['strategy']  == 'breath':
            options     = self.BreathFirstSearch(teamPick, simPlayers);

        else:
            print 'Draft Selection Type not Supported yet!'

        return(options)
    
    def SelectBetweenDraftOptions(self, options, teamPick):
        
        ''' Choose Between Multiple Draft Option Based on Team Tie Breaker '''
        
        draft   = self.teamStrategy.ix[teamPick]

        if draft['breakTie'] == 'random':
            select  = random.choice(options[options==True].index);

        elif draft['breakTie'] == 'first':
            select  = options[options==True].index[0];

        elif draft['breakTie'] == 'last':
            select  = options[options==True].index[-1];
            
        else:
            print 'Break Tie Type not Supported yet!'
 
        return(select);
        
    def SelectPlayerManually(self, simPlayers, name):
        
        ''' Let USER (Person) Choose which Player to Draft '''
        
        turns               = 0;
        MAX_TURNS           = 5;
        PLAYERS_TO_DISPLAY  = 20;
        
        # check if there is only one player left
        if self.teams[name]['pos'].count() == self.rounds - 1:
            options = simPlayers.pts == simPlayers.pts.max()
            print '\nYour last pick was:\n', simPlayers[options]
            return(options)
            
        print 'Your Team:\n', self.teams[name], '\nAvailable Players:\n',\
              simPlayers[:PLAYERS_TO_DISPLAY];
        while turns < MAX_TURNS:
            
            # Ask user to select player
            while True:
                turns   += 1;
                try:
                    select  = np.int64(raw_input('\nYo ' + name + \
                             ' Select a Player (use LHS index to select):\n'));
                    break;
                except ValueError:
                    print '\nOops!  That was not a valid number.\n'
                    print 'Please try (again) to Select a Player:', self.LONG_STR ;
                    
            # Check that user selected a valid player
            if simPlayers[simPlayers.index == select].empty:
                print '\nNo player with index = ' + str(select) +\
                      ', Please Select Again!\n';
            else:
                break;
                
        # Proceed to draft-max-player valid player never selected
        if turns == MAX_TURNS:
            print 'Okay, someone does not know how to draft!';
            print 'Do not worry, I will choose the player '\
                  'with the max projected points for you!';
            options     = simPlayers.pts == simPlayers.pts.max();
        else:
            options     = simPlayers.index.to_series() == select;
            
        return(options);
    
    def DepthFirstSearch(self, teamPick, simPlayers):
        
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
        playersOpt  = [];playersOpt.append(simPlayers.copy()); 
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
                
        options     = simPlayers.id == PLAYER_ID;
        
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
            playersOpt[0]   = self.DropProjectedPlayers(rnd[0], playersOpt[0], teamPick);
            pos.pop(0) if pos[0] == [] else 0;
            rnd[0]          += 1;
            
        # After selection update available simPlayers
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
            
        # If all nodes + branches have not been expanded
        if pos != []:
            self.DepthFirstSearchRecur(teamPick, pos, rnd, playersOpt, optionsTmp, optionsCmp)

    def GetBestDraftOptionFromBranch(self, options, CURRENT_RND):

        ''' Find player to draft based on max points '''
        
        # Set Initial Conditions
        maxPts      = 0
        PlayerID    = [];
        
        # High Water Mark Max Search Algorithm
        for df in options:
            if df.pts.sum() == maxPts and PlayerID.count(df.id[CURRENT_RND]) == 0:
                print 'AI Search found a tie - using randomly selecting tie-breaker...'
                PlayerID.append(df.id[CURRENT_RND])        # Add to selected player pool
                
            elif df.pts.sum() > maxPts:
                maxPts      = df.pts.sum()
                PlayerID    = [df.id[CURRENT_RND]]      # Clear all previously selected simPlayers
        
        return(PlayerID)    
           
    def BreathFirstSearch(self, teamPick, simPlayers):
        
        # Set Initial Conditions
        team        = self.teams[teamPick]
        playerTmp   = self.GetAvailablePlayers(simPlayers, team)
        nodes       = []; nodes.insert(0, playerTmp.pos.unique().tolist())
        playersOpt  = []; playersOpt.append(simPlayers.copy())
        optionsTmp  = []; optionsTmp.append(team.copy())
        optionsCmp  = list(optionsTmp); optionsCmp.pop(0)   # Empty Panel of completed teams 
        
        # Get all Draft Scenerio's
        self.BreathFirstSearchRecur(teamPick, nodes, playersOpt, optionsTmp, optionsCmp)
        
        # Find best player based on results
        PlayerID   = self.GetBestDraftOptionFromBranch(optionsCmp, team.pos.count())
        options    = simPlayers.id.isin(PlayerID)
        
        return(options)
        
    def BreathFirstSearchRecur(self, teamPick, nodes, playerList, draftList, draftCmp):        
 
        # Initial Conditions for Current Node
        THIS_WORKS_BETTER   = False
        simPlayers         = playerList.pop(0)
        draft           = draftList.pop(0)
        CURRENT_RND     = draft.pos.count()
        
        # Draft Based on Position Before Expanding (next) Node
        for pos in nodes.pop(0):
            
            # Push an untouched copy of simPlayers/team/round to top of list
            playerList.insert(0, simPlayers.copy())
            draftList.insert( 0,   draft.copy())
            
            # Add best player for pos to team
            playersAv       = simPlayers[simPlayers['pos'] == pos] 
            options         = playersAv.pts == playersAv.pts.max()
            select          = random.choice(options[options==True].index)
            self.PlacePlayerOnTeam(playersAv.ix[select], draftList[0], -2)

            # Update Total Players: Drop player and all simPlayers projected to be gone
            playerList[0]   = simPlayers.drop(select)
            playerList[0]   = self.DropProjectedPlayers(CURRENT_RND, playerList[0], teamPick, draftList[0])
 
            # Check if End of Branch           
            if CURRENT_RND == self.rounds-1:
                playerList.pop(0)
                draftCmp.insert(0,draftList.pop(0))
            else:
                if THIS_WORKS_BETTER == True:
                    # TODO: Find why does this work better?????
                    playerList[0]   = self.GetAvailablePlayers(playerList[0], draftList[0])
                    nodes.insert(0, playerList[0].pos.unique().tolist())
                else:
                    playerTmp       = self.GetAvailablePlayers(playerList[0], draftList[0])
                    nodes.insert(0, playerTmp.pos.unique().tolist())
                
        # Expand next branch if not exhausted
        if nodes != []:
            self.BreathFirstSearchRecur(teamPick, nodes, playerList, draftList, draftCmp)
        
    def DropProjectedPlayers(self, rnd, simPlayers, teamName, tmp):
        
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
        
        # Drop projected-to-be-gone-simPlayers
        playersLeft = simPlayers[numDropPlayers:]

        # Re-Add player by position if all have been removed
        for pos in simPlayers.pos.unique():
            if not playersLeft.pos[playersLeft.pos == pos].any():
                
                # Find Min Player for Pos
                playerOpt   = simPlayers[simPlayers.pos == pos]
                options     = playerOpt.pts.min() == playerOpt.pts
                select      = random.choice(options[options==True].index);
                
                playersLeft = playersLeft.append(simPlayers.ix[select]);
        
        return(playersLeft);
    
    def PlacePlayerOnTeam(self, player, team, i):
        
        RND     = team.pos.count()

        # Add Player to Team
        team.ix[RND]['pts']     = player['pts'];
        team.ix[RND]['pos']     = player['pos'];
        team.ix[RND]['id']      = player['id'];
        team.ix[RND]['pick']    = i+1;
        team.ix[RND]['posRnk']  = player['posRnk'];

    def AddPlayerToDraftResults(self, player, teamName):

        rnd     = self.teams[teamName]['pos'].count()
        i       = self.DraftResults['RND'].count() #+ 1
        
        self.DraftResults.ix[i]['RANK']  = player['rnk'];
        self.DraftResults.ix[i]['P_IDX'] = player.name
        self.DraftResults.ix[i]['RND']   = rnd
        self.DraftResults.ix[i]['TEAM']  = teamName;
        self.DraftResults.ix[i]['ID']    = player['id'];
        self.DraftResults.ix[i]['POS']   = player['pos'];
        self.DraftResults.ix[i]['PTS']   = player['pts'];
        
    def RunDraft(self, playersNew):

        # Draft Initial Conditions:
        self.CreateTeams();
        self.GenerateDraftOrder();
        self.CreateDraftResultStruct();
        
        # Create Local Copies        
        simPlayers     = playersNew.copy();

        # Start the Draft
        for i, teamPick in enumerate(self.DraftOrder):

            team        = self.teams[teamPick];             # TODO: MESSY TOO!
            select      = self.SelectPlayer(simPlayers, teamPick);
            
            self.PlacePlayerOnTeam(simPlayers.ix[select], team, i);
            self.AddPlayerToDraftResults(simPlayers.ix[select], teamPick);
            simPlayers     = simPlayers.drop(select);
            
    def GeneratePlayerDraftRanks(self, players):
        
        ''' Generate Player Draft Ranks by iterativly learning from AI '''
        
        COMPARE_RESULTS     = True
        STRATEGY_TO_USE     = 'breath'
        
        # Set all team strategy
        teamStrategySave    = self.teamStrategy.copy()
        self.teamStrategy['strategy'] = STRATEGY_TO_USE
        
        DraftResultDict     = {}

        for i in np.arange(self.RUNS_TO_LEARN):
            self.RunDraft(players)
            DraftResultDict[i+1]  = self.DraftResults
            players         = players.reindex(self.DraftResults.P_IDX)
            players['rnk']  = np.arange(len(players))
        
        # Add Initial Draft Ranks
        DraftResultDict[0]  = self.DraftResults.sort(columns='PTS',ascending=False)
        DraftResultDict[0].index = np.arange(self.DraftResults['ID'].count())

        if COMPARE_RESULTS:
            self.CompareDraftResults(pd.Panel(DraftResultDict))
    
        # Unset all team strategy to default
        self.teamStrategy = teamStrategySave
        print players
        return(players)
        
    def RunMultipleDrafts(self, simPlayers):
        
        '''Use to get statistical information from running multiple drafts'''
        
        # Create Empty Data Frames to save multi-run data
        playersAnalysis  = pd.DataFrame(index=simPlayers['id'].values, columns=['win', 'los', 'avg']).fillna(0);
        teamsAnalysis    = pd.DataFrame(index=self.teamNames,       columns=['win', 'los', 'avgPts', 'rnk']).fillna(0);
        
        teamsAnalysis.index.name        = 'team';
        playersAnalysis.index.name      = 'id';

        # Run-Multi Drafts and Gather Data
        # -----------------------------------------------------------
        print '\nDraft Simulation in progress!\nPlease be patient... Great Minds are at Work...\n',;
       
        for i in np.arange(self.DRAFTS_TO_RUN):

            # Kick off Draft
            self.RunDraft(simPlayers);
            
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
        
        return(playersAnalysis);
    
    def CompareDraftResults(self, DraftResultsPanel):
        
        ''' Clean way of analyzing multiple drafts '''
        
        DraftResultsDF  = DraftResultsPanel[4].copy()
        DraftResultsDF.pop('POS')
        DraftResultsDF.pop('RANK')
        # DraftResultsDF.pop('TEAM')
        #DraftResultsDF.pop('RND')
        DraftResultsDF.pop('ID')
        DraftResultsDF.pop('PTS')
        
        for i, df in enumerate(DraftResultsPanel):
            DraftResultsDF['ID'  + str(i)] =  DraftResultsPanel[i]['ID']
            DraftResultsDF['PTS' + str(i)] =  DraftResultsPanel[i]['PTS']
        
        print DraftResultsDF
        
        self.LOG.write(md.markdown('Player Pre-Rank Analysis:\n' + self.LONG_STR))
        self.LOG.write(DraftResultsDF.to_html())
        
        return(DraftResultsDF)
        
    def AnalyzeDraftResults(self, playersAnalysis, teamsAnalysis):
        
        GOOD_WIN_CHANCE         = 2 * 100 / self.numOfTeams;      # twice the average chance of winning
        MIN_RUNS_TO_PRINT       = self.DRAFTS_TO_RUN > 4;
        
        playersAnalysis         = playersAnalysis[playersAnalysis.avg != 0];        # Remove undrafted simPlayers:
        playersAnalysis         = playersAnalysis * 100 / self.DRAFTS_TO_RUN
        playersAnalysis['avg']  = playersAnalysis['avg'] / 100;
        
        teamsAnalysis['rnk']    = np.float16( teamsAnalysis['rnk']) / self.DRAFTS_TO_RUN;
        teamsAnalysis['avgPts'] = np.float64( teamsAnalysis['avgPts']) / self.DRAFTS_TO_RUN;

        # Print Analysis:
        print '\nLet\'s analyze some stats from the draft:\n', self.LONG_STR ;
 
        # Draft Complete!
        if self.PRINT_PLAYER_ANALYSIS == True and MIN_RUNS_TO_PRINT:
            print 'Win + Lose odds vs. player:\n', self.LONG_STR ;
            print playersAnalysis[:50].sort(columns='avg');
 
        if self.PRINT_PLOTS == True and MIN_RUNS_TO_PRINT:          
            if playersAnalysis[playersAnalysis > GOOD_WIN_CHANCE].dropna(how='all').empty:
                print 'Looks like no one has a strong statistical chance of winning...';
                playersAnalysis.plot(kind='bar', stacked=True);
            else:
                playersAnalysis[playersAnalysis > GOOD_WIN_CHANCE].dropna(how='all').plot(kind='bar', stacked=True);
            print 'Close figure to return'
            plt.show();
                
        if not MIN_RUNS_TO_PRINT:
            print '\nDraft Results By Team:\n', self.LONG_STR
            for name in self.teams:
                print 'TEAM ', name, ':\n', self.LONG_STR, self.teams[name]

        if self.PRINT_DRAFT_RESULTS == True and self.DRAFTS_TO_RUN < 5:
            print '\nDraft Results:\n', self.LONG_STR, self.DraftResults;    
        
        print self.LONG_STR, 'Okay let us take a look at how everyone did:\n', self.LONG_STR
        print teamsAnalysis.sort(columns='rnk', ascending=True), '\n', self.LONG_STR; 

        self.LOG.write(md.markdown('Draft Result by Team:\n' + self.LONG_STR))
        self.LOG.write(teamsAnalysis.sort(columns='rnk', ascending=True).to_html())

        self.LOG.write(md.markdown('Draft Result Evaluation:\n' + self.LONG_STR))
        self.LOG.write(self.DraftResults.to_html())
