import unittest, time
from ts17core import myrand, scene, gamemain


class MyRandTest(unittest.TestCase):
    def testRange(self):
        rand = myrand.MyRand()
        for _ in range(0, 1000):
            num = rand.rand()
            self.assertTrue(0 <= num < 1 << 32)

    def testReproduce(self):
        rand = myrand.MyRand(int(time.time()))
        seed = rand.rand()
        rand._seed = seed
        randList1 = [rand.rand() for _ in range(0, 1000)]
        rand._seed = seed
        randList2 = [rand.rand() for _ in range(0, 1000)]
        self.assertEqual(randList1, randList2)


class OctreeTest(unittest.TestCase):
    def setUp(self):
        self.tree = scene.Octree()

    def testBasic(self):
        sp1 = scene.Sphere((123456, 123456, 123456), 90000)
        sp2 = scene.Sphere((234567, 234567, 234567), 90000)
        self.tree.insert(sp1, 0)
        self.tree.insert(sp2, 1)
        sp3 = scene.Sphere((179011, 179011, 179011), 10000)
        self.assertEqual(self.tree.intersect(sp3, True), [])
        tmpResult = self.tree.intersect(sp3, False)
        tmpResult.sort()
        self.assertEqual(tmpResult, [0, 1])
        self.tree.delete(0)
        self.assertEqual(self.tree.intersect(sp3, False), [1])

    def testAgain(self):
        number = 100
        sqr = lambda x: x * x
        rand = myrand.MyRand()
        sp = []
        for i in range(number):
            sp.append(scene.Sphere(
                (rand.rand() % 800000 + 100000, rand.rand() % 800000 + 100000, rand.rand() % 800000 + 100000),
                rand.rand() % 100000))
            self.tree.insert(sp[i], i)
        for i in range(number):
            temp = []
            for j in range(number):
                if sqr(sp[i].center[0] - sp[j].center[0]) + sqr(sp[i].center[1] - sp[j].center[1]) + sqr(
                                sp[i].center[2] - sp[j].center[2]) < sqr(sp[i].radius):
                    temp.append(j)
            treeResult = self.tree.intersect(sp[i], True)
            treeResult.sort()
            self.assertEqual(treeResult, temp)
            temp = []
            for j in range(number):
                if sqr(sp[i].center[0] - sp[j].center[0]) + sqr(sp[i].center[1] - sp[j].center[1]) + sqr(
                                sp[i].center[2] - sp[j].center[2]) < sqr(sp[i].radius + sp[j].radius):
                    temp.append(j)
            treeResult = self.tree.intersect(sp[i], False)
            treeResult.sort()
            self.assertEqual(treeResult, temp)


class GameMaintest(unittest.TestCase):
    def setUp(self):
        self.game = gamemain.GameMain(0)
        self.player1 = gamemain.PlayerStatus()
        self.player2 = gamemain.PlayerStatus()
        self.player2.health = 1000
        self.player1.health = 1331
        self.game._players = {2: self.player2, 1: self.player1}
        self.game._scene.insert((scene.Sphere((10000, 10000, 10000), 10)), 2)
        self.game._scene.insert((scene.Sphere((10100, 10100, 10100), 11)), 1)

    def testMove(self):
        self.player2.speed = (1, 0, 0)
        self.game.update()
        self.assertEqual(self.game._scene.getObject(2).center, (100100, 10000, 10000))

    def testSkillShop(self):
        self.game.upgradeSkill(2, "longAttack")
        self.assertEqual(self.player2.ability,2, "money is not enough")
        self.assertEqual(self.player2.skills, {})
        self.player2.ability = 1
        self.game.upgradeSkill(2, "shield")
        self.assertEqual(self.player2.ability,2, "money is not enough")
        self.assertEqual(self.player2.skills, {})
        self.player2.ability = 10000
        for x in range(5):
            self.game.upgradeSkill(2, "longAttack")
            self.assertEqual(self.player2.ability, 10000 - 2 ** (x + 1) + 1, "ability is wrong")
            self.assertEqual(self.player2.skills, {"longAttack": x + 1})
        for x in range(5):
            self.game.upgradeSkill(2, "shortAttack")
            self.assertEqual(self.player2.ability, 9969 - 2 ** (x + 1), "ability is wrong")
            self.assertEqual(self.player2.skills, {"shortAttack": x + 1, "longAttack": 5})
        for x in range(5):
            self.game.upgradeSkill(2, "shield")
            self.assertEqual(self.player2.ability, 9937 - 2 ** (x + 2) - 4, "ability is wrong")
            self.assertEqual(self.player2.skills, {"shortAttack": 5, "longAttack": 5, "shield": x + 1})
        for x in range(5):
            self.game.upgradeSkill(2, "teleport")
            self.assertEqual(self.player2.ability, 9869 - 2 ** (x + 2) - 12, "ability is wrong")
            self.assertEqual(self.player2.skills, {"shortAttack": 5, "longAttack": 5, "shield": 5, "teleport": x + 1})
        for x in range(5):
            self.game.upgradeSkill(2, "visionUp")
            self.assertEqual(self.player2.ability, 9793 - 2 ** (x + 2) - 28, "ability is wrong")
            self.assertEqual(self.player2.skills,
                             {"shortAttack": 5, "longAttack": 5, "shield": 5, "teleport": 5, "visionUp": x + 1})
            self.assertEqual(self.player2.vision, 1000 + 500 * x)
        for x in range(5):
            self.game.upgradeSkill(2, "healthUp")
            self.assertEqual(self.player2.ability, 9701 - 2 ** (x + 1) - 30, "ability is wrong")
            self.assertEqual(self.player2.skills,
                             {"shortAttack": 5, "longAttack": 5, "shield": 5, "teleport": 5, "visionUp": 5,
                              "healthUp": x + 1})
            self.assertEqual(self.player2.health, 3500 + 2000 * x)
        self.game.upgradeSkill(2, "longAttack")
        self.assertEqual(self.player2.ability, 9639, "skill can't be improved")
        self.assertEqual(self.player2.skills,
                         {"shortAttack": 5, "longAttack": 5, "shield": 5, "teleport": 5, "visionUp": 5, "healthUp": 5})
        self.game.upgradeSkill(2, "shortAttack")
        self.assertEqual(self.player2.ability, 9639, "skill can't be improved")
        self.assertEqual(self.player2.skills,
                         {"shortAttack": 5, "longAttack": 5, "shield": 5, "teleport": 5, "visionUp": 5, "healthUp": 5})
        self.game.upgradeSkill(2, "shield")
        self.assertEqual(self.player2.ability, 9639, "skill can't be improved")
        self.assertEqual(self.player2.skills,
                         {"shortAttack": 5, "longAttack": 5, "shield": 5, "teleport": 5, "visionUp": 5, "healthUp": 5})
        self.game.upgradeSkill(2, "teleport")
        self.assertEqual(self.player2.ability, 9639, "skill can't be improved")
        self.assertEqual(self.player2.skills,
                         {"shortAttack": 5, "longAttack": 5, "shield": 5, "teleport": 5, "visionUp": 5, "healthUp": 5})
        self.game.upgradeSkill(2, "visionUp")
        self.assertEqual(self.player2.ability, 9639, "skill can't be improved")
        self.assertEqual(self.player2.skills,
                         {"shortAttack": 5, "longAttack": 5, "shield": 5, "teleport": 5, "visionUp": 5, "healthUp": 5})
        self.assertEqual(self.player2.vision, 3000)
        self.game.upgradeSkill(2, "healthUp")
        self.assertEqual(self.player2.ability, 9639, "skill can't be improved")
        self.assertEqual(self.player2.skills,
                         {"shortAttack": 5, "longAttack": 5, "shield": 5, "teleport": 5, "visionUp": 5, "healthUp": 5})
        self.assertEqual(self.player2.health, 11500)

    def testEat(self):
        now = self.player1.health
        self.player2.speed = (47, 47, 47)
        self.game.update()
        self.assertTrue(self.player1.health < now + 100)
        now = self.player1.health
        self.game.update()
        self.assertTrue(self.player1.health < now + 1100)
        self.assertTrue(self.player1.health >= now + 1000)
        self.assertNotIn(2, self.game._scene.intersect(self.game._scene.getObject(1)))

    def testshield_level4(self):
        self.player2.ability = 100
        for x in range(3):
            self.game.upgradeSkill(2, "shield")
        self.game.castSkill(2, "shield")
        self.player2.speed = (47, 47, 47)
        now = self.player1.health
        self.game.update()
        self.assertTrue(self.game._castSkills == {}, "castSkills is not empty")
        self.assertTrue(self.player1.health < now + 100)
        self.assertEqual(self.player2.shieldTime, 160)
        now = self.player1.health
        self.game.update()
        self.assertTrue(self.player1.health < now + 100)
        self.assertTrue(2 in self.game._scene.intersect(self.game._scene.getObject(1)))
        self.assertEqual(self.player2.shieldTime, 159)
        self.player2.speed = (0, 0, 0)
        now = self.player1.health
        for x in range(158):
            self.game.update()
            self.assertTrue(self.player1.health < now + 100)
            self.assertTrue(2 in self.game._scene.intersect(self.game._scene.getObject(1)))
            self.assertEqual(self.player2.shieldTime, 158 - x)
            self.now = self.player1.health
        now1 = self.player2.health
        self.game.update()
        self.assertTrue(self.player1.health < now + 1100)
        self.assertTrue(self.player1.health >= now + now1)
        self.assertTrue(2 not in self.game._scene.intersect(self.game._scene.getObject(1)))

    def tsetshortattack(self):
        self.player2.speed=(50,50,50);
        self.update();
        self.player2.speed=(0,0,0);
        self.game.upgradeSkill(2, "shortAttack")
        self.game.castSkill(2, "shortAttack")
        self.assertTrue(self.player2.health>=1000,"shortAttack to fast")
        self.update()
        self.assertTrue(self.player1.health<331+100,"shortAttack is wrong")
        self.assertTrue(self.player2.health<1000,"shortAtack without cost")

    def testteleport(self):
        self.game.upgradeSkill(2,"teleport")
        self.game.castSkill(2,"teleport",((10010, 10010, 10010)))
        self.assertTrue(self.game.playerpos(2)==(10000,10000,10000),"teleport to fast")
        self.game.update()
        self.assertTrue(self.game.playerpos(2)==(10010,10010,10010),"teleport wrong")

    def testlongAttack(self):
        self.game.upgradeSkill(2,"longAttack")
        self.game.castSkill(2,"longAttack",((1, 1, 1)))
        self.assertTrue(self.player2.health==1000,"longAttack to fast")
        self.game.update()
        self.assertTrue(self.player1.health>1331,"longAttack speed is wrong")
        temp=self.player1.health
        self.game.update()
        self.assertTrue(self.player1.health<temp-50,"longAttack is wrong")

