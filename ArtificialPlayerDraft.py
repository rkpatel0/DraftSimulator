
import numpy as np;
import pandas as pd;
import ffa.draft_simulator as draft;
import ffa.create_players as players;
import ffa.get_players as playersReal;
import ffa.scratch_sheet as tmp;

# -------------------------------------------------------
# Generate Draft Information:
# -------------------------------------------------------

# 1. Generate Data
#--------------------------------------------------------
# Player Frame/Classes
pColumns  = ['QB', 'RB', 'WR', 'TE']        # columns
nSpots    = [   1,    2,    2,    1]
rSlope    = [  15,   15,    5,    5]
rStart    = [ 400,  400,  400,  250]
pIndex    = ['spots', 'slope', 'start'];

# Team Data Panel
tcol      =            [     'strategy'  , 'breakTie' ];  
draftData = np.reshape(['A',  'rank',      'random'   ,\
                        'RDP', 'rank',     'random'   ,\
                        'RKP', 'rank',   'random'   ,\
                        'D',   'rank',     'random'   ,\
                        ], (4,3))

# Generate Data Frames...
posArray    = np.reshape([nSpots,rSlope, rStart],(3,4));
posFrame    = pd.DataFrame(posArray, columns=pColumns,index=pIndex);
draftInfo   = pd.DataFrame(draftData[:,1:], index=draftData[:,0], columns=tcol)

# Create Classes:
oGp         = players.CreatePlayers(posFrame, len(draftInfo.index));
oD          = draft.DraftSimulator(posFrame, draftInfo);
oP          = playersReal.GetPlayers();
players     = oP.GetSeasonStats(2012)
playersNew  = oP.CleanPlayersForDraftSim(players);


# Parameters to modify...
oD.DRAFTS_TO_RUN  = 100;

playersAnalysis = oD.RunMultipleDrafts(oGp.players);
    
print 'done!'