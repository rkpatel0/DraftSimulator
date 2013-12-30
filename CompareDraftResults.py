
import numpy as np;
import pandas as pd;
import ffa.draft_simulator as draft;
import ffa.create_players as players;
import ffa.get_players as playersReal;
import ffa.scratch_sheet as tmp;

# -------------------------------------------------------
# Generate Draft Information:
# -------------------------------------------------------

# 1. Draft Settings
#--------------------------------------------------------
pColumns  = ['QB', 'RB', 'WR', 'TE']       
nSpots    = [   1,    2,    2,    1]
rSlope    = [  5,   20,    5,   20]
rStart    = [ 400,  350,  325,  300]
pIndex    = ['spots', 'slope', 'start'];

posArray    = np.reshape([nSpots,rSlope, rStart],(3,4));
posFrame    = pd.DataFrame(posArray, columns=pColumns,index=pIndex);

# 2. Team Settings
#--------------------------------------------------------
tcol      =            [       'strategy'   , 'breakTie' ];  
teamData  = np.reshape(['A'   ,  'breath'     , 'random'   ,\
                        'B'   ,  'breath'     , 'random'   ,\
                        'C'   ,  'breath'     , 'random'   ,\
                        'D'   ,  'breath'     , 'random'   ,\
                        'E'   ,  'breath'     , 'random'   ,\
                        'F'   ,  'breath'     , 'random'   ,\
                        'G'   ,  'breath'     , 'random'   ,\
                        'H'   ,  'breath'     , 'random'   ,\
                        ], (8,3))

draftInfo   = pd.DataFrame(teamData[:,1:], index=teamData[:,0], columns=tcol)

# 3. Generate Player Class
#--------------------------------------------------------
oGp         = players.CreatePlayers(posFrame, len(draftInfo.index));

oP          = playersReal.GetPlayers();
players     = oP.GetSeasonStats(2011)
players     = oP.CleanPlayersForDraftSim(players);

# 4. Run Drafts to Compare
#--------------------------------------------------------
DraftResultDict     = {}

oD                  = draft.DraftSimulator(posFrame, draftInfo);
oD.DRAFTS_TO_RUN    = 1

# Set Initial Draft Ranks:
players.sort(columns='rnk',ascending=True,inplace=True);
#players.sort(columns='pts',ascending=False,inplace=True);

playersAnalysis     = oD.RunMultipleDrafts(players);
DraftResultDict[0]  = oD.DraftResults

playersAnalysis     = oD.RunMultipleDrafts(players.reindex(oD.DraftResults.RANK));
DraftResultDict[1]  = oD.DraftResults

playersAnalysis     = oD.RunMultipleDrafts(players.reindex(oD.DraftResults.RANK));
DraftResultDict[2]  = oD.DraftResults

playersAnalysis     = oD.RunMultipleDrafts(players.reindex(oD.DraftResults.RANK));
DraftResultDict[3]  = oD.DraftResults

playersAnalysis     = oD.RunMultipleDrafts(players.reindex(oD.DraftResults.RANK));
DraftResultDict[4]  = oD.DraftResults
DraftResultDict[5]  = players[:48].sort(columns='rnk',ascending=True)

oD.CompareDraftResults(pd.Panel(DraftResultDict))
    
print 'done!'