
import numpy as np;
import pandas as pd;
import ffa.draft_simulator as draft;
import ffa.create_players as simPlayers;
from ffa import get_players as playersReal
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
PosInfo    = pd.DataFrame(posArray, columns=pColumns,index=pIndex);

# 2. Team Settings
#--------------------------------------------------------
tcol      =            [         'strategy'   , 'breakTie' ];  
teamData  = np.reshape(['AI'   ,  'rank'     , 'random'   ,\
                        'Alpa' , 'rank'     , 'random'   ,\
                        'C'   ,  'rank'     , 'random'   ,\
                        'D'   ,  'rank'     , 'random'   ,\
                        'E'   ,  'rank'     , 'random'   ,\
                        'F'   ,  'rank'     , 'random'   ,\
                        'G'   ,  'breath'     , 'random'   ,\
                        'H'   ,  'rank'     , 'random'   ,\
                        ], (8,3))

TeamInfo   = pd.DataFrame(teamData[:,1:], index=teamData[:,0], columns=tcol)

# 3. Generate Player Class
#--------------------------------------------------------
oGp         = simPlayers.CreatePlayers(PosInfo, len(TeamInfo.index));

oP          = playersReal.GetPlayers();
simPlayers     = oP.GetSeasonStats(2011)
simPlayers     = oP.CleanPlayersForDraftSim(simPlayers);
#simPlayers.sort(columns='pts',ascending=False,inplace=True);

# 4. Kick-Off Draft
#--------------------------------------------------------
oD                  = draft.DraftSimulator(PosInfo, TeamInfo);
oD.DRAFTS_TO_RUN    = 1
playersAnalysis     = oD.RunMultipleDrafts(oGp.players);

print 'done!'