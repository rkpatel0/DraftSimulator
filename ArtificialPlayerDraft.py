
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
tcol      =            [         'strategy'   , 'breakTie' ];  
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
players     = oP.GetSeasonStats(2012)
players     = oP.CleanPlayersForDraftSim(players);
players.sort(columns='pts',ascending=False,inplace=True);

# 4. Kick-Off Draft
#--------------------------------------------------------
oD                  = draft.DraftSimulator(posFrame, draftInfo);
oD.DRAFTS_TO_RUN    = 1
playersAnalysis     = oD.RunMultipleDrafts(players);

print 'done!'