from ..comm.pwm import PWM
from time import sleep

""" joint_key convention:
    R - right, L - left
    F - front, M - middle, B - back
    H - hip, K - knee, A - Ankle
    key : (channel, minimum_pulse_length, maximum_pulse_length) """

joint_properties = {

    'LFH': (2, 248, 398), 'LFK': (1, 188, 476), 'LFA': (0, 131, 600),
    'LMH': (6, 312, 457), 'LMK': (5, 251, 531), 'LMA': (4, 138, 598),
    'LBH': (10, 315, 465), 'LBK': (9, 166, 466), 'LBA': (8, 140, 620),
    'RFH': (29, 275, 425), 'RFK': (30, 227, 507), 'RFA': (31, 160, 625),
    'RMH': (25, 240, 390), 'RMK': (26, 230, 514), 'RMA': (27, 150, 620),
    'RBH': (21, 320, 480), 'RBK': (22, 209, 499), 'RBA': (23, 150, 676),
    'N': (15, 150, 650)
}

driver1 = PWM(0x40)
driver2 = PWM(0x70)

driver1.setPWMFreq(60)
driver2.setPWMFreq(60)


def drive(ch, val):
    driver = driver1 if ch < 16 else driver2
    ch = ch if ch < 16 else ch - 16
    driver.setPWM(ch, 0, val)


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def remap(old_val, old_range, new_range):
    old_min, old_max = old_range
    new_min, new_max = new_range
    new_diff = (new_max - new_min)*(old_val - old_min) / float((old_max - old_min))
    return int(round(new_diff)) + new_min


class HexapodCore:

    def __init__(self):

        self.neck = Joint("neck", 'N')

        self.left_front = Leg('left front', 'LFH', 'LFK', 'LFA')
        self.right_front = Leg('right front', 'RFH', 'RFK', 'RFA')

        self.left_middle = Leg('left middle', 'LMH', 'LMK', 'LMA')
        self.right_middle = Leg('right middle', 'RMH', 'RMK', 'RMA')

        self.left_back = Leg('left back', 'LBH', 'LBK', 'LBA')
        self.right_back = Leg('right back', 'RBH', 'RBK', 'RBA')

        self.legs = [self.left_front, self.right_front,
                     self.left_middle, self.right_middle,
                     self.left_back, self.right_back]

        self.right_legs = [self.right_front, self.right_middle, self.right_back]
        self.left_legs = [self.left_front, self.left_middle, self.left_back]

        self.tripod1 = [self.left_front, self.right_middle, self.left_back]
        self.tripod2 = [self.right_front, self.left_middle, self.right_back]

        self.hips, self.knees, self.ankles =[],[],[]

        for leg in self.legs:
            self.hips.append(leg.hip)
            self.knees.append(leg.knee)
            self.ankles.append(leg.ankle)

    def off(self):

        self.neck.off()

        for leg in self.legs:
            leg.off()


class Leg:

    def __init__(self, name, hip_key, knee_key, ankle_key):

        max_hip, max_knee, knee_leeway = 45, 50, 10

        self.hip = Joint("hip", hip_key, max_hip)
        self.knee = Joint("knee", knee_key, max_knee, leeway = knee_leeway)
        self.ankle = Joint("ankle", ankle_key)

        self.name = name
        self.joints = [self.hip, self.knee, self.ankle]

    def pose(self, hip_angle = 0, knee_angle = 0, ankle_angle = 0):

        self.hip.pose(hip_angle)
        self.knee.pose(knee_angle)
        self.ankle.pose(ankle_angle)

    def move(self, knee_angle = None, hip_angle = None, offset = 100):
        """ knee_angle < 0 means thigh is raised, ankle's angle will be set to the specified
            knee angle minus the offset. offset best between 80 and 110 """

        if knee_angle == None: knee_angle = self.knee.angle
        if hip_angle is None: hip_angle = 0

        self.pose(hip_angle, knee_angle, knee_angle - offset)

    def replant(self, raised, floor, offset, t = 0.1):

        self.move(raised)
        sleep(t)

        self.move(floor, offset)
        sleep(t)

    def off(self):
        for joint in self.joints:
            joint.off()

    def __repr__(self):
        return 'leg: ' + self.name


class Joint:

    def __init__(self, joint_type, jkey, maxx = 90, leeway = 0):

        self.joint_type, self.name =  joint_type, jkey
        self.channel, self.min_pulse, self.max_pulse = joint_properties[jkey]
        self.max, self.leeway = maxx, leeway

        self.off()

    def pose(self, angle = 0):

        angle = constrain(angle, -(self.max + self.leeway), self.max + self.leeway)
        pulse = remap(angle, (-self.max, self.max), (self.min_pulse, self.max_pulse))

        drive(self.channel, pulse)
        self.angle = angle

        #print repr(self), ':', 'pulse', pulse

    def off(self):
        drive(self.channel, 0)
        self.angle = None

    def __repr__(self):
        return 'joint: ' + self.joint_type + ' : ' + self.name + ' angle: ' + str(self.angle)