import machine
import micropython
import time

red_led     = machine.Pin(1)
green_led   = machine.Pin(2)
blue_led    = machine.Pin(3)
orange_len  = machine.Pin(4)

pulse_detected_led = red_led


class Tachometer(object):

    NUM_SAMPLES = 16

    def __init__(self, timer_num, channel_num, pin_name, pulses_per_rev=2):
        self.timestamp = [0] * Tachometer.NUM_SAMPLES
        self.num_samples = -1
        self.delta_time = 0
        self.idx = 0
        self.pulses_per_rev = pulses_per_rev
        self.pulse_detected = False

        # Setup the timer to run at 1MHz
        # We assume that we're running on a 32-bit timer).
        if timer_num != 2 and timer_num != 5:
            raise ValueError("Tachometer needs a 32-bit timer")
        self.timer = machine.Timer(timer_num)
        print("Initializing timer")
        self.timer.init(mode=Timer.PERIODIC, freq=1000, callback=channel_callback)
        #self.timer.init(prescaler=(int(self.timer.source_freq() / 1000000) - 1), period=0x1fffffff)

        self.pin = machine.Pin(pin_name)

        print("Initializing channel")
        self.channel = self.timer.channel(channel_num, machine.Timer.IC,
                                          pin=self.pin,
                                          polarity=machine.Timer.RISING)
        self.channel.callback(self.channel_callback)
        print("self.channel =", self.channel)
        print("Initialization done")

    def channel_callback(self, tim):
        """The channel callback gets called everytime there is an edge on
           the pin this channel is hooked up to.
        """
        if pulse_detected_led:
            #pulse_detected_led.toggle() no toggle
       #self.pulse_detected = True
        self.pulse_timestamp = self.channel.capture() & 0x1fffffff
        if self.num_samples < Tachometer.NUM_SAMPLES:
            prev_timestamp = self.timestamp[0]
            self.num_samples += 1
        else:
            prev_timestamp = self.timestamp[self.idx]
        self.timestamp[self.idx] = self.pulse_timestamp
        if self.pulse_timestamp < prev_timestamp:
            prev_timestamp -= 0x20000000
        self.delta_time = self.pulse_timestamp - prev_timestamp
        self.idx = (self.idx + 1) % Tachometer.NUM_SAMPLES

    def dump(self):
        ts = [0] * Tachometer.NUM_SAMPLES
        machine.disable_irq()
        for i in range(Tachometer.NUM_SAMPLES):
            ts[i] = self.timestamp[i]
        last_pulse = self.pulse_timestamp
        delta_time = self.delta_time
        num_samples = self.num_samples
        machine.enable_irq()
        print("last_pulse =", last_pulse)
        print("delta_time =", delta_time)
        print("num_samples =", num_samples)
        for i in range(Tachometer.NUM_SAMPLES):
            print("ts[%d] = %d" % (i, ts[i]))

    def rpm(self):
        if not self.pulse_detected:
            return 0
        timer_count = self.timer.counter() & 0x1fffffff
        last_pulse = self.pulse_timestamp
        if timer_count < last_pulse:
            last_pulse -= 0x20000000
        if (timer_count - last_pulse) > 1000000:
            # No pulses in the past second.
            self.pulse_detected = False
            #print("timer_count =",  timer_count, "last_pusle =",  last_pulse)
            #self.dump()
            return 0
        machine.disable_irq()
        delta_time = self.delta_time
        num_samples = self.num_samples
        machine.enable_irq()
        if delta_time == 0 or self.pulses_per_rev == 0:
            return 0
        print (str(num_samples * 1000000 * 60 / (delta_time * self.pulses_per_rev)))
        return num_samples * 1000000 * 60 / (delta_time * self.pulses_per_rev)
    

def test():
    """Test program - assumes X2 is jumpered to X1."""
    micropython.alloc_emergency_exception_buf(100)

    print("Starting tach")
    tach = Tachometer(timer_num=2, channel_num=1, pin_name=22)

    print("Starting pulses")
    t5 = machine.Timer(5, freq=4)
    oc_pin = machine.Pin.board.X2
    oc = t5.channel(2, machine.Timer.OC_TOGGLE, pin=oc_pin)

    for freq in range(0, 600, 100):
        if freq == 0:
            freq = 1
        else:
            t5.freq(freq * 4)   # x 2 for toggle, x2 for 2 pulses_per_rev
        time.sleep(1000)
        print("RPM =",  tach.rpm(), "Freq =", freq, " as RPM =", freq * 60)

    # stop the pulses
    print("Stopping pulses")
    oc_pin.init(machine.Pin.OUT_PP)
    # wait for 1.5 seconds
    time.sleep(1500)
    print("RPM =",  tach.rpm())
    print("RPM =",  tach.rpm())

    print("Starting pulses again")
    # start the pulses up again
    oc = t5.channel(2, machine.Timer.OC_TOGGLE, pin=oc_pin)
    time.sleep(2000)
    print("RPM =",  tach.rpm())
    print("RPM =",  tach.rpm())


#u6 = machine.UART(6, 115200)
#machine.repl_uart(u6)
tach = Tachometer(timer_num=2, channel_num=1, pin_name=22)
#test()


