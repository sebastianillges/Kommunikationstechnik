from numpy import array as vector
from random import choices, seed, randint
from komm import PSKModulation, RectangularPulse, TransmitFilter, AWGNChannel, QAModulation
import numpy as np
import scipy as sp
from math import pi
import matplotlib.pyplot as plt


def gen_bit_vector(k):
    return vector(choices([0, 1], k=k))


def pulse_shaping(pulse, symV, nsamp):
    filt = TransmitFilter(pulse, nsamp)
    return filt(symV) / nsamp


def amplitude_modulation(s, fc, fs):
    t = vector(range(0, len(s)))
    cos_carrier = np.cos(2 * pi * fc / fs * t)
    sin_carrier = np.sin(2 * pi * fc / fs * t)
    return np.real(s) * cos_carrier + np.imag(s) * sin_carrier


def amplitude_demodulation(s, fc, fs):
    t = vector(range(0, len(s)))
    cos_carrier = np.cos(2 * pi * fc / fs * t)
    sin_carrier = np.sin(2 * pi * fc / fs * t)
    return s * cos_carrier + 1j * s * sin_carrier


def lowpass(s, fs, fg):
    n = len(s)
    f = np.fft.fftfreq(n, 1 / fs)
    zeroI = np.nonzero(abs(f) > fg)
    s_fft = sp.fft.fft(s)
    s_fft[zeroI] = 0
    return np.fft.ifft(s_fft)


def integrate_and_dump(s, nsamp):
    return [sum(s[i:i + nsamp]) for i in range(0, len(s), nsamp)]


def main():
    # parameter
    doPlot = True
    noise_levelL = ['symbol', 'baseband', 'passband']
    noise_level = 2
    print('noise level:', noise_levelL[noise_level])
    theSeed = 2
    seed(theSeed)
    np.random.seed(randint(0, 10000))

    # input bits
    k = 10
    # symbol duration
    Tsymb = 1
    fsymb = 1 / Tsymb  # symbol rate
    nsamp = 32  # sampling points per symbol
    fc = 4  # carrier frequency
    fs = 64  # sampling rate
    Ts = 1 / fs  # time between sampling points

    # modulation scheme
    mod_scheme = PSKModulation(4)
    # pulse shape
    pulse = RectangularPulse()

    # channel
    SNRdB = 50  # SNR in decibel
    SNR = 10 ** (SNRdB / 10)  # linear SNR
    awgn_sym = AWGNChannel(SNR, 1)  # AWGN channel for simulation on symbol level
    awgn_bb = AWGNChannel(SNR, 1 / nsamp)  # AWGN channel for simulation on baseband signal level
    awgn_fb = AWGNChannel(SNR, 0.25 / nsamp)  # AWGN channel for simulation on frequency band signal level

    # simulation
    bitV = gen_bit_vector(k)  # generate random bits
    print('original bits:', bitV, sep='\n', end='\n\n')
    symV = mod_scheme.modulate(bitV)  # generate symbols (digital modulation)
    print('original symbols:', symV, sep='\n', end='\n\n')
    if noise_levelL[noise_level] == 'symbol':
        noisy_symV = awgn_sym(symV)  # add noise
        print('noisy symbols:', noisy_symV, sep='\n', end='\n\n')
    else:
        # generate baseband signal
        inphase_signal = pulse_shaping(pulse, np.real(symV), nsamp)
        quadrature_signal = pulse_shaping(pulse, np.imag(symV), nsamp)
        bb_signal = inphase_signal + 1j * quadrature_signal  # generate signal from in_phase and quadrature component
        if noise_levelL[noise_level] == 'baseband':
            noisy_bb_signal = awgn_bb(bb_signal)  # add noise
            print('noisy signal:', noisy_bb_signal, sep='\n', end='\n\n')
        else:
            # generate frequency band signal (amplitude modulation)
            fb_signal = amplitude_modulation(bb_signal, fc, fs)
            noisy_fb_signal = awgn_fb(fb_signal)  # add noise
            print('noisy signal:', noisy_fb_signal, sep='\n', end='\n\n')
            # recover baseband signal
            noisy_bbx_signal = amplitude_demodulation(noisy_fb_signal, fc, fs)
            noisy_bb_signal = lowpass(noisy_bbx_signal, fs, fc) * 2
        # recover symbols
        noisy_symV = integrate_and_dump(noisy_bb_signal, nsamp)
        print('recovered symbols:', noisy_symV, sep='\n', end='\n\n')
    # recover bits
    noisy_bitV = mod_scheme.demodulate(noisy_symV)
    print('recovered bits:', noisy_bitV, sep='\n', end='\n\n')

    # plot results
    if doPlot:
        # Constellation diagram
        plt.figure()
        plt.scatter(np.real(symV), np.imag(symV), label='Original Symbols', alpha=0.5)
        plt.scatter(np.real(noisy_symV), np.imag(noisy_symV), label='Recovered Symbols', alpha=0.5)
        plt.title("Constellation Diagram")
        plt.xlabel("In-phase")
        plt.ylabel("Quadrature")
        plt.legend()
        plt.grid(True)
        plt.show()

        # Original baseband signal
        plt.figure(figsize=(10, 6))
        plt.subplot(2, 1, 1)
        plt.plot(np.real(bb_signal))
        plt.title("Original Baseband Signal - In-Phase Component")
        plt.subplot(2, 1, 2)
        plt.plot(np.imag(bb_signal))
        plt.title("Original Baseband Signal - Quadrature Component")
        plt.subplots_adjust(hspace=0.5)

        # Noisy baseband signal
        plt.figure(figsize=(10, 6))
        plt.subplot(2, 1, 1)
        plt.plot(np.real(noisy_bb_signal))
        plt.title("Noisy Baseband Signal - In-Phase Component")
        plt.subplot(2, 1, 2)
        plt.plot(np.imag(noisy_bb_signal))
        plt.title("Noisy Baseband Signal - Quadrature Component")
        plt.subplots_adjust(hspace=0.5)

        plt.show()


def run_simulation_study():
    def simulate_modulation(k, fc, fs, nsamp, SNRdB, modulation_order):
        # Set the seed for reproducibility
        seed(2)
        np.random.seed(randint(0, 10000))

        # Ensure k is a multiple of modulation_order
        bits_per_symbol = int(np.log2(modulation_order))
        if k % bits_per_symbol != 0:
            k += bits_per_symbol - (k % bits_per_symbol)

        # Generate random bits
        bitV = gen_bit_vector(k)

        # Define modulation scheme
        if modulation_order <= 4:
            mod_scheme = PSKModulation(modulation_order)
        else:
            mod_scheme = QAModulation(modulation_order)

        # Modulate the bits
        symV = mod_scheme.modulate(bitV)

        # Pulse shaping
        pulse = RectangularPulse()
        inphase_signal = pulse_shaping(pulse, np.real(symV), nsamp)
        quadrature_signal = pulse_shaping(pulse, np.imag(symV), nsamp)
        bb_signal = inphase_signal + 1j * quadrature_signal

        # Amplitude modulation
        fb_signal = amplitude_modulation(bb_signal, fc, fs)

        # AWGN channel
        SNR = 10 ** (SNRdB / 10)
        awgn_fb = AWGNChannel(SNR, 0.5 / nsamp)
        noisy_fb_signal = awgn_fb(fb_signal)

        # Amplitude demodulation
        noisy_bbx_signal = amplitude_demodulation(noisy_fb_signal, fc, fs)
        noisy_bb_signal = lowpass(noisy_bbx_signal, fs, fc) * 2

        # Recover symbols
        noisy_symV = integrate_and_dump(noisy_bb_signal, nsamp)

        # Demodulate symbols
        noisy_bitV = mod_scheme.demodulate(noisy_symV)

        # Calculate bit error rate
        ber = np.sum(bitV != noisy_bitV) / len(bitV)

        return bitV, symV, noisy_symV, noisy_bitV, ber

    # Parameters
    fc = 4  # carrier frequency
    fs = 64  # sampling rate
    nsamp = 32  # samples per symbol
    modulation_order = 4  # QPSK

    # Study with varying SNR values
    snr_values = range(5, 30, 5)
    ber_values = []

    # Perform simulation with high SNR and few symbols
    # k_values = [200, 400]
    k_values = [200]
    for snr in snr_values:
        for k in k_values:
            bitV, symV, noisy_symV, noisy_bitV, ber = simulate_modulation(k, fc, fs, nsamp, snr, modulation_order)
            print(f'Bit Error Rate for k={k}, SNRdB={snr}: {ber}')
            print('Original bits:', bitV)
            print('Recovered bits:', noisy_bitV)

            # Plot constellation diagrams
            plt.figure()
            plt.scatter(np.real(symV), np.imag(symV), label='Original Symbols', alpha=0.5)
            plt.scatter(np.real(noisy_symV), np.imag(noisy_symV), label='Recovered Symbols', alpha=0.5)
            plt.title(f"Constellation Diagram (k={k}, SNR={snr}dB)")
            plt.xlabel("In-phase")
            plt.ylabel("Quadrature")
            plt.tight_layout()
            plt.legend()
            plt.grid(True)
            plt.show()

    snr_values = range(5, 30, 2)
    k = 10000
    for SNRdB in snr_values:
        _, _, _, _, ber = simulate_modulation(k, fc, fs, nsamp, SNRdB, modulation_order)
        ber_values.append(ber)

    # Plot BER vs SNR
    plt.figure()
    # plt.semilogy(snr_values, ber_values, 'o-')
    plt.plot(snr_values, ber_values, 'o-')
    plt.title("BER vs SNR for QPSK")
    plt.xlabel("SNR (dB)")
    plt.ylabel("Bit Error Rate (BER)")
    plt.tight_layout()
    plt.grid(True)
    plt.show()

    # Study with different modulation schemes
    modulation_orders = [2, 4, 16, 64]
    ber_modulation = {}

    for mod_order in modulation_orders:
        ber_values = []
        for SNRdB in snr_values:
            _, _, _, _, ber = simulate_modulation(k, fc, fs, nsamp, SNRdB, mod_order)
            ber_values.append(ber)
        ber_modulation[mod_order] = ber_values

    # Plot BER vs SNR for different modulation schemes
    plt.figure()
    for mod_order in modulation_orders:
        # plt.semilogy(snr_values, ber_modulation[mod_order], label=f'{mod_order}-QAM', marker='o')
        plt.plot(snr_values, ber_modulation[mod_order], label=f'{mod_order}-QAM', marker='o')
    plt.title("BER vs SNR for different modulation schemes")
    plt.xlabel("SNR (dB)")
    plt.ylabel("Bit Error Rate (BER)")
    plt.tight_layout()
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    main()
    run_simulation_study()
