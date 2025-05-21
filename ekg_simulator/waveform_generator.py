import neurokit2 as nk
import numpy as np

class WaveformGenerator:
    def __init__(self):
        pass

    def get_ekg_segment(self, duration_seconds=10, sampling_rate=100, heart_rate=70, 
                        st_depression_mv=0.0, st_elevation_mv=0.0, qrs_amplitude_factor=1.0,
                        t_wave_amplitude_factor=1.0, target_qt_duration_ms=440,
                        target_pr_interval_ms=160, target_qrs_duration_ms=100,
                        osborn_wave_present=False):
        """
        Generates an EKG signal segment.
        Includes placeholders for ST depression/elevation, QRS/T-wave amp, QT/PR/QRS duration, Osborn waves.
        """
        # print(f"WaveformGenerator: HR={heart_rate}, QT_target={target_qt_duration_ms}, T_amp_factor={t_wave_amplitude_factor}")
        ekg_signal = nk.ecg_simulate(
            duration=duration_seconds,
            sampling_rate=sampling_rate,
            heart_rate=heart_rate,
            method="ecgsyn" # ecgsyn is known to vary QT/PR/QRS with HR
        )

        # Apply QRS and T-wave amplitude factors first, as ST changes are additive
        if qrs_amplitude_factor != 1.0:
            # Simple approach: scale the entire signal for QRS amplitude.
            ekg_signal = ekg_signal * qrs_amplitude_factor
            
        if t_wave_amplitude_factor != 1.0:
            # Very rough approximation for T-wave amplitude change: scale entire signal slightly.
            # This is a placeholder due to ecgsyn limitations for specific wave component scaling.
            # A more accurate implementation would require signal delineation and targeted scaling.
            # Example: If t_wave_amplitude_factor is 2.0, scale signal by 1.1 (10% increase)
            # This is a very simplified approach.
            simplified_t_wave_scaling = 1.0 + ( (t_wave_amplitude_factor - 1.0) * 0.1 ) # e.g. factor 2.0 -> 1.1, factor 0.5 -> 0.95
            if simplified_t_wave_scaling != 1.0 :
                ekg_signal = ekg_signal * simplified_t_wave_scaling
            # print(f"Note: T-wave amplitude factor ({t_wave_amplitude_factor}) applied as simplified global scaling ({simplified_t_wave_scaling:.2f}). This is a placeholder.")

        # ST Segment Modification Logic
        if st_elevation_mv > 0:
            # print(f"Applying ST elevation: {st_elevation_mv} mV")
            ekg_signal += st_elevation_mv  # Global upward shift
        elif st_depression_mv > 0: # Check for depression only if no elevation
            # print(f"Applying ST depression: {st_depression_mv} mV")
            ekg_signal -= st_depression_mv  # Global downward shift


        # QT Duration Note
        # NeuroKit2's ecgsyn method inherently adjusts the QT interval based on the heart rate.
        # Direct setting of the QT duration is not supported by this generation method.
        # Bradycardia (lower heart_rate) will naturally lead to a longer QT interval.
        if target_qt_duration_ms != 440: # 440 is a typical baseline, not necessarily the default if other conditions changed it
             # print(f"WaveformGenerator: Target QT duration received: {target_qt_duration_ms}ms. Actual QT in 'ecgsyn' is strongly coupled with HR ({heart_rate}bpm).")
             pass
        if target_pr_interval_ms != 160:
             pass
             # print(f"Note: Target PR interval set to {target_pr_interval_ms}ms. Actual PR is primarily influenced by heart rate ({heart_rate}bpm) in the 'ecgsyn' model.")
        if target_qrs_duration_ms != 100:
             pass
             # print(f"Note: Target QRS duration set to {target_qrs_duration_ms}ms. Actual QRS is primarily influenced by heart rate ({heart_rate}bpm) in the 'ecgsyn' model.")
            
        return ekg_signal
