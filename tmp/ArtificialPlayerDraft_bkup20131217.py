
import numpy as np;
import pandas as pd;
import ffa.draft_simulator as draft;
import ffa.create_players as players;
import ffa.scratch_sheet as tmp;

# -------------------------------------------------------
# Generate Draft Information:
# -------------------------------------------------------

# 1. Generate Data
#--------------------------------------------------------
# Player Frame/Classes
pColumns  = ['QB', 'RB', 'WR', 'TE']        # columns
nSpots    = [   0,    1,    2,    0]
rSlope    = [  10,   15,   10,    5]
rStart    = [ 420,  450,  400,  250]
pIndex    = ['spots', 'slope', 'start'];

# Team Data Panel
tcol      =            [     'strategy'  , 'breakTie' ];  
draftData = np.reshape(['A', 'max_points', 'random'   ,\
                        'B', 'max_points', 'random'   ,\
                        'C', 'max_points', 'random'   ,\
                        'D', 'max_points', 'random'   ,\
                        ], (4,3))

# Generate Data Frames...
posArray    = np.reshape([nSpots,rSlope, rStart],(3,4));
posFrame    = pd.DataFrame(posArray, columns=pColumns,index=pIndex);
draftInfo   = pd.DataFrame(draftData[:,1:], index=draftData[:,0], columns=tcol)

# Create Classes:
oGp         = players.GetPlayers(posFrame, len(draftInfo.index));
oD          = draft.DraftSimulator(posFrame, draftInfo);

# Parameters to modify...
oD.DRAFTS_TO_RUN  = 100;

oD.CreateTeams();

oD.BreathFirstSearch(oD.teams['A'], oGp.players)
# Run Simulation...
print 'hello'
#playersAnalysis = oD.RunMultipleDrafts(oGp.players);