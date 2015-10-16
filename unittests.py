#!/usr/bin/python
# -*- coding: UTF-8 -*-

from ttSchweizer import *


import unittest

class TestSpieler(unittest.TestCase):

  def test_numberOfSiege(self):
    A = Spieler('A',1)
    B = Spieler('B',2)
    C = Spieler('C',3)

    A.addMatch(B, MatchResult(3,0))
    A.addMatch(C, MatchResult(0,3))

    siege = A.getNumberOfSiege()

    self.assertEquals(1, siege)

  def test_getOponents(self):
    A = Spieler('A',1)
    B = Spieler('B',2)
    C = Spieler('C',3)

    A.addMatch(C, MatchResult(0,3))
    A.addMatch(B, MatchResult(3,0))

    self.assertEquals([C,B], A.getOponents())

  def test_findOponentOnlyOneIsPossible(self):
    A = Spieler('A',1)
    B = Spieler('B',2)
    groups = GroupeOfPlayersWithSameSieganzahl([[B]])

    self.assertEquals(B, A.findOponent(groups))

    C = Spieler('C',3)
    groups = GroupeOfPlayersWithSameSieganzahl([[B],[C]])
    A.addMatch(B, MatchResult(3,0))
    
    self.assertEquals(C, A.findOponent(groups))

  def test_findOponentNoOneIsPossible(self):
    A = Spieler('A',1)
    B = Spieler('B',2)
    A.addMatch(B, MatchResult(3,0))
    groups = GroupeOfPlayersWithSameSieganzahl([[B]])

    self.assertEquals(None, A.findOponent(groups))

  def test_findOponentOneIsNotPossibleRegardingLaterDrawings(self):
    A = Spieler('A',1)
    B = Spieler('B',2)
    C = Spieler('C',2)
    # The next players all played against B
    U = Spieler('U',2)
    V = Spieler('V',2)
    W = Spieler('W',2)
    X = Spieler('X',2)
    B.addMatch(U, MatchResult(3,0))
    B.addMatch(V, MatchResult(3,0))
    B.addMatch(W, MatchResult(3,0))
    B.addMatch(X, MatchResult(3,0))
    groups = GroupeOfPlayersWithSameSieganzahl([[C], [B,U,V,W,X]])

    self.assertNotEquals(None, A.findOponent(groups))
    self.assertNotEquals(C, A.findOponent(groups))


class TestBegegnungen(unittest.TestCase):

  def setupRound1(self, allPlayers):
    allPlayersList = []
    for name,ttr in (('A',11), ('B',10), ('C',1), ('D',9), ('E',2), ('F',8), ('G',3), ('H',7), ('I',6), ('K',4), ('L',5)):
        allPlayersList.append(allPlayers.spieler(name,ttr))

    allPlayersList.append(allPlayers.freilos())

    (A,B,C,D,E,F,G,H,I,K,L,Freilos) = allPlayersList


    H.addFreilos(Freilos)
    for p1, p2, s1, s2 in ((A,K,3,0), (B,G,3,1), (D,L,3,0), (F,C,2,3), (I,E,3,2)):
        theMatchResult = MatchResult(s1, s2)
        p1.addMatch(p2, theMatchResult)
        p2.addMatch(p1, theMatchResult.turned())

    return allPlayersList

  def test_getRanking(self):
    allPlayers = Spieler_Collection()
    (A,B,C,D,E,F,G,H,I,K,L,Freilos) = self.setupRound1(allPlayers)

    # Spieler: A, B, C, D, E, F, G, H, I, K, L
    # ttr:    11 10  1  9  2  8  3  7  6  4  5 
    # Siege:   1  1  1  1  0  0  0  1  1  0  0
    # Buchh.:  0  0  0  0  0  0  0  0  0  0  0
    # Platz:   6  5  1  4  7 11  8  3  2  9 10

    ranking = allPlayers.getRanking()

    self.assertEquals(11, len(ranking))  # 11 Spieler

    spieler, siege, buchholzzahl, platz = ranking[0]
    self.assertEquals(C, spieler); self.assertEquals(1, siege); self.assertEquals(0, buchholzzahl)
    self.assertEquals(1, platz)

    expected = [(C,1,0,1),(I,1,0,2),(H,1,0,3),(D,1,0,4),(B,1,0,5),(A,1,0,6),(E,0,0,7),(G,0,0,8),(K,0,0,9),(L,0,0,10),(F,0,0,11)]
    self.assertEquals(expected, ranking)

  def test_groupContainsAllPlayer(self):
    allPlayers = Spieler_Collection()
    (A,B,C,D,E,F,G,H,I,K,L,Freilos) = self.setupRound1(allPlayers)

    groups = allPlayers.getGroupBySiege()

    self.assertEquals(set(allPlayers.values()), set(groups.getAllPlayers()))

  def test_groupTop_returnsAndRemovesTop(self):
    allPlayers = Spieler_Collection()
    (A,B,C,D,E,F,G,H,I,K,L,Freilos) = self.setupRound1(allPlayers)

    groups = allPlayers.getGroupBySiege()

    for player in (A,B,D,H,I,C,F,L,K,G,E,Freilos,None):
        self.assertEquals(player, groups.top())

  def test_removeElementFromGroup(self):
    groups = GroupeOfPlayersWithSameSieganzahl()
    groups.append([1,2,3])
    groups.append([10,20])
    groups.rm(10)

    self.assertEquals([1,2,3], groups[0])
    self.assertEquals([20], groups[1])

    groups.rm(20)
    self.assertEquals(1, len(groups))
    self.assertEquals([1,2,3], groups[0])


  def test_groupBySiege(self):
    allPlayers = Spieler_Collection()
    (A,B,C,D,E,F,G,H,I,K,L,Freilos) = self.setupRound1(allPlayers)

    groups = allPlayers.getGroupBySiege()

    self.assertEquals(3, len(groups))
    self.assertEquals([A,B,D,H,I,C], groups[0])
    self.assertEquals([F,L,K,G,E], groups[1])
    self.assertEquals([Freilos], groups[2])

  def test_getBegegnungenAllCanBeInSameGroup(self):

    allPlayers = Spieler_Collection()
    (A,B,C,D,E,F,G,H,I,K,L,Freilos) = self.setupRound1(allPlayers)

    groups = allPlayers.getGroupBySiege()
    begegnungen = allPlayers.getBegegnungen(groups)

    self.assertEquals(6, len(begegnungen))
    winner = [player for begegnung in begegnungen[:3] for player in begegnung]
    self.assertEquals(set([A,B,D,H,I,C]), set(winner))
    looser = [player for begegnung in begegnungen[3:] for player in begegnung]
    self.assertEquals(set([F,L,K,G,E,Freilos]), set(looser))
    


class TestMatchResult(unittest.TestCase):

  def test_onlyGamesMatchResult_doubleTurned_areEqual(self):
    res = MatchResult(3,1)  
    self.assertEqual(res, res.turned().turned())
    self.assertEqual(MatchResult(1,3), res.turned())
    self.assertNotEqual(MatchResult(1,3), res)

  def test_gamesMatchResultIncludingPoints_doubleTurned_areEqual(self):
    res = MatchResult(2,3, ('10',11,'-3','-5','-8'))  
    self.assertEqual(res, res.turned().turned())

  def test_gamesMatchResultIncludingPoints_zeroSpecialHandling(self):
    res = MatchResult(3,2, (10,11,-3,'-0',8))  
    self.assertEqual(MatchResult(2,3, (-10,-11,3,0,-8)), res.turned())

  def test_isWon(self):
    res = MatchResult(3,1)  
    self.assertTrue(res.isWon())
    self.assertFalse(res.turned().isWon())


if __name__ == '__main__':
    unittest.main()
