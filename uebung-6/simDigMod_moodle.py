from numpy import array as vector
from random import choices, seed, randint
from komm import PSKModulation, RectangularPulse, TransmitFilter, AWGNChannel
import numpy as np
import scipy as sp
from math import pi

import matplotlib.pyplot as plt


def gen_bit_vector(k):
    return vector(choices([0,1],k=k))


def pulse_shaping(pulse,symV,nsamp):
    filt=TransmitFilter(pulse,nsamp)
    return filt(symV)/nsamp       


def amplitude_modulation(s,fc,fs):
    t=vector(range(0,len(s)))
    cos_carrier=np.cos(2*pi*fc/fs*t)
    sin_carrier=np.sin(2*pi*fc/fs*t)
    return np.real(s)*cos_carrier+np.imag(s)*sin_carrier


def amplitude_demodulation(s,fc,fs):
    t=vector(range(0,len(s)))
    cos_carrier=np.cos(2*pi*fc/fs*t)
    sin_carrier=np.sin(2*pi*fc/fs*t)
    return s*cos_carrier+1j*s*sin_carrier


def lowpass(s,fs,fg):
    n=len(s)
    f=np.fft.fftfreq(n,1/fs)
    zeroI=np.nonzero(abs(f)>fg)
    s_fft=sp.fft.fft(s)
    s_fft[zeroI]=0
    return np.fft.ifft(s_fft)


def integrate_and_dump(s,nsamp):
    return [sum(s[i:i+nsamp]) for i in range(0,len(s),nsamp)]


def main():
    # parameter
    doPlot=True
    noise_levelL=['symbol','baseband','passband']
    noise_level=2
    print('noise level:', noise_levelL[noise_level])
    theSeed=2
    seed(theSeed)
    np.random.seed(randint(0,10000))

    # input bits
    k=20
    # symbol duration
    Tsymb=1
    fsymb=1/Tsymb   # symbol rate
    nsamp=32    # sampling points per symbol
    fc=4*fsymb  # carrier frequency relative to symbol rate
    fs=nsamp/Tsymb # sampling rate
    Ts=1/fs # time between sampling points

    # modulation scheme
    mod_scheme=PSKModulation(4)
    # pulse shape
    pulse=RectangularPulse()

    # channel
    SNRdB=20    # SNR in decibel
    SNR=10**(SNRdB/10)  # linear SNR
    awgn_sym=AWGNChannel(SNR,1) # AWGN channel for simulation on symbol level
    awgn_bb=AWGNChannel(SNR,1/nsamp) # AWGN channel for simulation on baseband signal level
    awgn_fb=AWGNChannel(SNR,0.25/nsamp) # AWGN channel for simulation on frequency band signal level

    # simulation
    bitV=gen_bit_vector(k)  # generate random bits
    print('original bits:', bitV, sep='\n', end='\n\n')
    symV=mod_scheme.modulate(bitV)  # generate symbols (digital modulation)
    print('original symbols:', symV, sep='\n', end='\n\n')
    if noise_levelL[noise_level]=='symbol':
        noisy_symV=awgn_sym(symV)   # add noise
        print('noisy symbols:', noisy_symV, sep='\n', end='\n\n')
    else:
        # generate baseband signal
        inphase_signal=pulse_shaping(pulse,np.real(symV),nsamp)
        quadrature_signal=pulse_shaping(pulse,np.imag(symV),nsamp)
        bb_signal=inphase_signal+1j*quadrature_signal # generate signal from in_phase and quadrature component
        if noise_levelL[noise_level]=='baseband':
            noisy_bb_signal=awgn_bb(bb_signal)  # add noise
            print('noisy signal:', noisy_bb_signal, sep='\n', end='\n\n')
        else:
            # generate frequency band signal (amplitude modulation)
            fb_signal=amplitude_modulation(bb_signal,fc,fs)
            noisy_fb_signal=awgn_fb(fb_signal)  # add noise
            print('noisy signal:', noisy_fb_signal, sep='\n', end='\n\n')
            # recover baseband signal
            noisy_bbx_signal=amplitude_demodulation(noisy_fb_signal,fc,fs)
            noisy_bb_signal=lowpass(noisy_bbx_signal,fs,fc)*2
        # recover symbols
        noisy_symV=integrate_and_dump(noisy_bb_signal,nsamp)
        print('recovered symbols:', noisy_symV, sep='\n', end='\n\n')
    # recover bits
    noisy_bitV=mod_scheme.demodulate(noisy_symV)
    print('recovered bits:', noisy_bitV, sep='\n', end='\n\n')

    # plot results



if __name__ == '__main__':
    main()
