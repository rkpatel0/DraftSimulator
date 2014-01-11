
import numpy as np;
import pandas as pd;
import ffa.draft_simulator as draft;
import ffa.create_players as genPlayers;
import ffa.get_players as getPlayers;
import ffa.scratch_sheet as tmp;

# -------------------------------------------------------
# Generate Draft Information:
# -------------------------------------------------------

# 1.  League Settings
#--------------------------------------------------------
pColumns  = ['QB', 'RB', 'WR', 'TE']       
nSpots    = [   1,   2,     0,    1]
rSlope    = [  35,   20,    5,   10]
rStart    = [ 400,   400, 325,  300]
pIndex    = ['spots', 'slope', 'start'];

posArray  = np.reshape([nSpots,rSlope, rStart],(3,4));
PosInfo   = pd.DataFrame(posArray, columns=pColumns,index=pIndex);

# 2. Team Settings
#--------------------------------------------------------
tcol      =            [       'strategy'   , 'breakTie' ];  
teamData  = np.reshape(['A'   ,  'rank'     , 'random'   ,\
                        'B'   ,  'rank'     , 'random'   ,\
                        'C'   ,  'rank'     , 'random'   ,\
                        'D'   ,  'breath'   , 'random'   ,\
                        'E'   ,  'rank'     , 'random'   ,\
                        'F'   ,  'rank'     , 'random'   ,\
                        'G'   ,  'rank'     , 'random'   ,\
                        'H'   ,  'rank'     , 'random'   ,\
                        ], (8,3))

TeamInfo   = pd.DataFrame(teamData[:,1:], index=teamData[:,0], columns=tcol)

oD         = draft.DraftSimulator(PosInfo, TeamInfo);
oD.DRAFTS_TO_RUN    = 1

# 3. Generate Player Class
#--------------------------------------------------------

USE_REAL_PLAYERS = True

if USE_REAL_PLAYERS:
    oGetP       = getPlayers.GetPlayers();
    players     = oGetP.GetSeasonStats(2010)
else:
    oGenP       = genPlayers.CreatePlayers(PosInfo, len(TeamInfo.index));
    players     = oGenP.GeneratePlayers()

# 4. Run Drafts to Compare
#--------------------------------------------------------

oD.RunMultipleDrafts(players)
#players.sort(columns='pts',ascending=False,inplace=True);
players = oD.GeneratePlayerDraftRanks(players)
oD.RunMultipleDrafts(players.sort_index());
    
print 'done!'