import unittest
from ai import AI
from world import World
from car import Car
import random
import math

def margin(speed):
    return 4 + speed * 0.1

class MyTestCase(unittest.TestCase):

    def test_speedChangeStack(self):
        world = World()
        ai = AI(world)
        vl = 10
        ap = 1.7
        an = -1.9
        ai._addDebugProfileStackCount('_calculateMidSpeedWithDistanceOnly1')
        ai._addDebugProfileStackCount('_calculateSpeedLimitedConstantSpeedTime')
        ai._addDebugProfileStackCount('_calculateLowMidSpeedWithEqualAccelerations')
        ai._addDebugProfileStackCount('_calculateANASpeeditems')
        ai._addDebugProfileStackCount('_calculateACASpeeditems')
        ai._addDebugProfileStackCount('_calculateHighMidSpeed')
        ai._addDebugProfileStackCount('_calculateTimeFromConstantSpeedToConstantAcceleration')
        ai._addDebugProfileStackCount('_calculateLinearAccelerationTime')
        ai._addDebugProfileStackCount('_calculateFloorSpeed')
        ai._addDebugProfileStackCount('_calculateRoofSpeed')
        ai._addDebugProfileStackCount('vt >= vl')
        ai._addDebugProfileStackCount('no change')
        for vi in range(0, vl+1):
            for vt in range(0,vl+1):
                for d in range(1,50):
                    for tt in range(1,20):
                        for vit in range(1,vl+1):
                            if vit == vt: continue
                            ptarget = Car(vit)
                            ptarget.addAcceleration((vt - vit)/tt, tt)
                            vt, dt, _ = ptarget.getTargetSpeedAndDistanceAndTimeToIt()
                            profile = Car(vi)
                            speedchange = ai._speedChangeStack(vi, vt, vl, d, dt, tt, ap, an)
                            offset = 0.0
                            for acc, dur in speedchange.accelerations:
                                profile.addAcceleration(acc, dur, offset)
                                offset += dur
                            vtt, dtt, ttt = profile.getTargetSpeedAndDistanceAndTimeToIt()
                            self.assertIsNotNone(profile)
                            time = max(tt, ttt)
                            d1 = profile.getTravelDistance(time)
                            d2 = ptarget.getTravelDistance(time)
                            if vt < vl:
                                msg = f'\nvit={vit}\nvi={vi} \nvt={vt} \nvl={vl} \nd={d} \ndt={dt} \ntt={tt} \nap={ap} \nan={an}\n'
                                self.assertAlmostEqual(d1, d2+d, msg=msg+f'{ai.debug}')
                            else:
                                msg = f'\nvit={vit}\nvi={vi} \nvt={vt} \nvl={vl} \nd={d} \ndt={dt} \ntt={tt} \nap={ap} \nan={an}\n'
                                self.assertGreaterEqual(d2+d, d1-1e-6, msg=msg+f'{ai.debug}')
        print(ai.debug['stack'])

    def test_speedChageStackWithSingleArgs(self):
        world = World()
        ai = AI(world)
        vit = 2
        vi = 0
        vt = 1.0
        vl = 10
        d = 1
        dt = 1.5
        tt = 9
        ap = 1.7
        an = -1.9
        ptarget = Car(vit)
        ptarget.addAcceleration((vt - vit) / tt, tt)
        vt, dt, tt = ptarget.getTargetSpeedAndDistanceAndTimeToIt()
        profile = Car(vi)
        speedchange = ai._speedChangeStack(vi, vt, vl, d, dt, tt, ap, an)
        offset = 0.0
        for acc, dur in speedchange.accelerations:
            profile.addAcceleration(acc, dur, offset)
            offset += dur
        vtt, dtt, ttt = profile.getTargetSpeedAndDistanceAndTimeToIt()
        self.assertIsNotNone(profile)
        time = max(tt, ttt)
        d1 = profile.getTravelDistance(time)
        d2 = ptarget.getTravelDistance(time)
        if vt < vl:
            msg = f'\nvit={vit}\nvi={vi} \nvt={vt} \nvl={vl} \nd={d} \ndt={dt} \ntt={tt} \nap={ap} \nan={an}\n'
            self.assertAlmostEqual(d1, d2 + d, msg=msg + f'{ai.debug}')
        else:
            msg = f'\nvit={vit}\nvi={vi} \nvt={vt} \nvl={vl} \nd={d} \ndt={dt} \ntt={tt} \nap={ap} \nan={an}\n'
            self.assertGreaterEqual(d2 + d, d1 - 1e-6, msg=msg + f'{ai.debug}')

    def test_speedChageStackWithSingleArgsxx(self):
        world = World()
        ai = AI(world)
        vit = 2
        vi = 0
        vt = 1.0
        vl = 10
        d = 1
        dt = 1.5
        tt = 9
        ap = 1.7
        an = -1.9
        for tt in range(1,100):
            for vt in range(20):
                for vit in range(20):
                    if vt == vit:
                        continue
                    ptarget = Car(vit)
                    ptarget.addAcceleration((vt - vit) / tt, tt)
                    vt, dt1, tt1 = ptarget.getTargetSpeedAndDistanceAndTimeToIt()
                    msg = f'\ntt={tt}\nvt={vt}\nvit={vit}'
                    self.assertEqual(tt, tt1, msg)

    def test_speedChageStackWithSingleArgsxx1231231(self):
        tt = 1
        vt = 0.0
        vit = 1
        ptarget = Car(vit)
        ptarget.addAcceleration((vt - vit) / tt, tt)
        vt, dt1, tt1 = ptarget.getTargetSpeedAndDistanceAndTimeToIt()
        msg = f'\ntt={tt}\nvt={vt}\nvit={vit}'
        self.assertEqual(tt, tt1, msg)

    def test_speedChageStackWithSingleArgs1(self):
        world = World()
        ai = AI(world)
        vi = 0
        vt = 1.0
        vl = 10
        d = 1
        dt = 1.5
        tt = 9
        ap = 1.7
        an = -1.9
        profile = Car(vi)
        speedchange = ai._speedChangeStack(vi, vt, vl, d, dt, tt, ap, an)
        vmax, vmin = speedchange.getMaxMinSpeed()
        self.assertGreater(vl, vmax - 1e-6)
        profile.addSpeedChanges(speedchange)


    def test_speedchangeargs(self):
        world = World()
        ai = AI(world)
        vi = 16.666666666666668
        vt = 0
        vl = 16.666666666666668
        d = -0.6484823333254894
        dt = 0
        tt = 0
        ap = 1.7
        an = -1.9
        ai._speedChangeStack(vi,vt,vl,d,dt,tt,ap,an)

    def test_speedchangeargs1(self):
        world = World()
        ai = AI(world)
        vi = 13.25136612021858
        vt = 0
        vl = 16.666666666666668
        d = 76.79859122158535
        dt = 0.3243595980867724
        tt = 0.5843211068246816
        ap = 1.7
        an = -1.9
        origd = 94.87704918032787
        res = ai._speedChangeStack(vi,vt,vl,d,dt,tt,ap,an)
        t = res.getTimeToTargetSpeed()
        trd = res.getTravelDistance(t)
        print(res, trd+origd)

    def test_speedChangesToAdjustToCarAhead11(self):
        world = World()
        ai = AI(world)
        vl = 20
        vi = 5
        cl = 4
        car = Car(vi)
        car.addAcceleration(-1,4)
        car.addAcceleration(1,4,4)
        d = 10
        sc = ai._speedChangesToAdjustToCarAhead(car, vi, vl, d, 2, -2, margin, cl)
        print(sc.accelerations)
        t = max(sc.getTimeToTargetSpeed(), car.getTimeToTargetSpeed())
        print(sc.getTimeToTargetSpeed(), car.getTimeToTargetSpeed())
        s = 0
        while s < t*10:
            step = s*0.1
            da = car.getTravelDistance(step)
            db = sc.getTravelDistance(step)
            m = margin(min(car.getSpeed(step), sc.getSpeed(step)))
            print(step, da+d - (db+car.halflength*2))
            self.assertGreater(da+d, db+car.halflength*2)
            s += 1

    def test_somecalculations(self):
        world = World()
        ai = AI(world)
        a1=2
        a2=-2
        vi=0
        vt=1
        d=4
        vm1 = math.sqrt((2 * a1 * a2 * d + a2 * vi * vi - a1 * vt * vt) / (a2 - a1))
        vm2 = math.sqrt((d + vi * vi / (2 * a1) - vt * vt / (2 * a2)) / (1 / (2 * a1) - 1 / (2 * a2)))
        tt = (vm1-vi)/a1+(vt-vm2)/a2
        t=tt+1
        d=5
        vm3 = ai._calculateMidSpeed(vi, vt, d, t, a1, a2)
        print(vm1,vm2,vm3)

    def test_speedChangesToAdjustToCarAhead1(self):
        world = World()
        ai = AI(world)
        vl = 20
        ap = 1.7
        an = -1.9
        va = 1
        d = 20
        vt = 15
        tt = 41
        vb = 10
        car = Car(va)
        car.changeSpeed(vt, tt/2)
        car.changeSpeed(0, tt/2, tt/2)
        car.changeSpeed(vt, tt/2, tt)
        car.changeSpeed(0, tt/2, 3*tt/2)
        speedchange = ai._speedChangesToAdjustToCarAhead1(car, vb, vl, d, ap, an, dummymarginfunc)
        margin = car.halflength + dummymarginfunc(0)
        print(speedchange)
        time  =0
        step = 1
        for i in range(int(tt/step)+80):
            time += step
            d1 = car.getTravelDistance(time)
            d2 = speedchange.getTravelDistance(time)
            print(round(time,4), round(d1+d-margin-d2,4), round(speedchange.getSpeed(time),2), round(car.getSpeed(time),2))
        print(ai.debug)
        self.assertAlmostEqual(car.getTravelDistance(time)+d-margin, speedchange.getTravelDistance(time))

def dummymarginfunc(speed):
    return 4

if __name__ == '__main__':
    unittest.main()
