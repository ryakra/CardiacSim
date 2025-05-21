import numpy as np

class PhysiologicalEffectsManager:
    def __init__(self):
        """
        Manages the physiological effects on EKG parameters.
        """
        # Can store default or baseline EKG parameters if needed,
        # but for now, most are derived or passed in physiological_state.
        self.baseline_qrs_amplitude_factor = 1.0

    def update_ekg_parameters(self, physiological_state):
        """
        Updates EKG parameters based on the current physiological state,
        simulating effects like hypovolemic shock and tension pneumothorax.

        Args:
            physiological_state (dict): A dictionary containing current physiological data,
                                      e.g., {'blood_volume_percent': 100, 
                                             'heart_rate_bpm': 70,
                                             'tension_pneumothorax_present': False,
                                             'qrs_amplitude_factor': 1.0}.

        Returns:
            dict: A dictionary with target EKG parameters,
                  e.g., {'target_heart_rate': new_hr, 
                         'target_st_depression_mv': new_st_depression,
                         'target_qrs_amplitude_factor': new_qrs_factor}.
        """
        blood_volume_percent = physiological_state.get('blood_volume_percent', 100)
        # Get current heart rate, which might have been affected by previous states (e.g. initial setting)
        # or use a baseline if not set.
        current_heart_rate = physiological_state.get('heart_rate_bpm', 70) 
        
        # Initialize with current values or defaults
        target_heart_rate = current_heart_rate 
        target_st_depression_mv = physiological_state.get('st_depression_mv', 0.0)
        target_qrs_amplitude_factor = self.baseline_qrs_amplitude_factor

        if blood_volume_percent > 90:
            # Class I: No significant change
            # Target HR remains base_heart_rate, ST depression = 0
            pass # Already set
        elif 75 <= blood_volume_percent <= 90:
            # Class II: Mild shock
            target_heart_rate = base_heart_rate * np.random.uniform(1.1, 1.2)
            target_st_depression_mv = 0.05
        elif 60 <= blood_volume_percent < 75:
            # Class III: Moderate shock
            target_heart_rate = base_heart_rate * np.random.uniform(1.2, 1.4)
            target_st_depression_mv = 0.1
        elif blood_volume_percent < 60:
            # Class IV: Severe shock
            target_heart_rate = base_heart_rate * np.random.uniform(1.4, 1.7)
            # Cap heart rate to a maximum plausible value, e.g., 220 bpm
            target_heart_rate = min(target_heart_rate, 220) 
            target_st_depression_mv = 0.2
        
        # Tension Pneumothorax Logic
        # This is applied *after* hypovolemia effects on HR, potentially overriding/enhancing them.
        if physiological_state.get('tension_pneumothorax_present', False):
            # Increase HR significantly due to tension pneumothorax
            # Using max ensures it's at least the shock-induced HR or the pneumo-induced HR.
            # The problem states: target_heart_rate = max(target_heart_rate, physiological_state.get('heart_rate_bpm', 70) * 1.5)
            # Here, physiological_state.get('heart_rate_bpm', 70) is the *current* HR, not necessarily the original baseline.
            # It's better to use the target_heart_rate calculated from hypovolemia as the base for this comparison.
            pneumo_hr_effect = current_heart_rate * 1.5 # Tentative HR if pneumo was the ONLY factor on baseline
            target_heart_rate = max(target_heart_rate, pneumo_hr_effect) 
            target_heart_rate = max(target_heart_rate, 120) # Ensure it's at least 120 as a minimum for pneumo.
            
            target_qrs_amplitude_factor = 0.5  # Low voltage
        else:
            target_qrs_amplitude_factor = self.baseline_qrs_amplitude_factor # Normal voltage

        # Ensure heart rate is an integer
        target_heart_rate = int(round(target_heart_rate))
        # Cap heart rate again after all effects
        target_heart_rate = min(target_heart_rate, 220)

        # Cap heart rate again after all effects
        # target_heart_rate = min(target_heart_rate, 220) # This was already here, let's ensure it's applied after all HR mods

        # TBI/ICP Logic
        target_t_wave_amplitude_factor = physiological_state.get('t_wave_amplitude_factor', 1.0)
        target_qt_duration_ms = physiological_state.get('qt_duration_ms', 440)
        # Initialize st_elevation_mv which might be set by blast injury logic
        target_st_elevation_mv = physiological_state.get('st_elevation_mv', 0.0)


        if physiological_state.get('tbi_present', False) and physiological_state.get('icp_mmhg', 10) > 20:
            # Bradycardia (Cushing Reflex)
            # Ensure HR is low but not below a certain floor (e.g. 40), and respects other conditions.
            # min(target_heart_rate, 55) will try to bring HR down if it's higher.
            # max(40, ...) ensures it doesn't go too low.
            target_heart_rate = max(40, min(target_heart_rate, 55))
            
            target_t_wave_amplitude_factor = 2.0  # Prominent T-waves
            target_qt_duration_ms = 500  # QT Prolongation
        else:
            # Reset to baseline or current state if TBI/ICP condition not met
            # This should ideally not overwrite if another condition (like blast) is setting them
            if not physiological_state.get('blast_injury_present', False) or not physiological_state.get('coronary_age_suspected', False): # check if blast is not setting T-wave
                target_t_wave_amplitude_factor = 1.0 
            # Similar check for QT
            if not physiological_state.get('blast_injury_present', False) or not physiological_state.get('coronary_age_suspected', False): # check if blast is not setting QT
                target_qt_duration_ms = physiological_state.get('qt_duration_ms', 440) # or a more dynamic baseline

        # Blast Injury/AGE Logic
        # Initialize target_st_elevation_mv, default to current state or 0
        # target_st_elevation_mv is already initialized above using physiological_state.get('st_elevation_mv', 0.0)
        
        if physiological_state.get('blast_injury_present', False) and \
           physiological_state.get('coronary_age_suspected', False):
            
            # Tachycardia for AGE
            target_heart_rate = max(target_heart_rate, 110) 
            
            # ST Elevation for MI-like pattern
            target_st_elevation_mv = 0.2 
            
            # Precedence Logic: ST elevation overrides ST depression
            if target_st_elevation_mv > 0:
                target_st_depression_mv = 0.0
        else:
            # If AGE is not suspected, st_elevation_mv should be 0 unless another condition sets it.
            # For now, assume only AGE causes elevation.
            target_st_elevation_mv = 0.0 
            # target_st_depression_mv would have been determined by hypovolemia logic earlier,
            # and should not be overridden here unless blast/AGE was active and is now not.

        # Hyperkalemia Logic
        serum_k = physiological_state.get('serum_k_meq_l', 4.0)
        # target_t_wave_amplitude_factor is already initialized from previous logic or state
        target_pr_ms = physiological_state.get('pr_interval_ms', 160)
        target_qrs_ms = physiological_state.get('qrs_duration_ms', 100)

        if serum_k > 5.5:  # Mild Hyperkalemia
            target_t_wave_amplitude_factor = max(target_t_wave_amplitude_factor, 1.5)
        if serum_k > 6.5:  # Moderate Hyperkalemia
            target_t_wave_amplitude_factor = max(target_t_wave_amplitude_factor, 2.0)
            target_pr_ms = 240
            target_qrs_ms = 120
            target_heart_rate = min(target_heart_rate, 70) # Apply bradycardic effect
        if serum_k > 7.5:  # Severe Hyperkalemia
            target_t_wave_amplitude_factor = max(target_t_wave_amplitude_factor, 2.5)
            target_pr_ms = 300
            target_qrs_ms = 160
            target_heart_rate = min(target_heart_rate, 60) # More pronounced bradycardia

        # Final HR cap
        target_heart_rate = min(target_heart_rate, 220)

        # Hypocalcemia Logic
        serum_ca_mg_dl = physiological_state.get('serum_ca_mg_dl', 9.5)
        # target_qt_duration_ms is already initialized from previous logic (e.g. TBI) or state
        
        # Use the current physiological_state's qt_duration_ms as the baseline for max comparison
        # This ensures that if another condition (like TBI) has already prolonged QT, 
        # hypocalcemia will only make it longer if its effect is greater.
        current_qt_target_from_state = physiological_state.get('qt_duration_ms', 440)

        if serum_ca_mg_dl < 7.0: # Severe Hypocalcemia
            target_qt_duration_ms = max(current_qt_target_from_state, 520)
        elif serum_ca_mg_dl < 8.5: # Mild Hypocalcemia
            target_qt_duration_ms = max(current_qt_target_from_state, 480)
        # Else (Normal Calcium): target_qt_duration_ms remains as determined by other conditions or baseline
        # No explicit 'else' needed if we initialize target_qt_duration_ms with the value from other effects

        # Hypothermia Logic
        temp_c = physiological_state.get('core_body_temperature_celsius', 37.0)
        target_osborn_wave_present = False
        
        # Use current physiological_state values as baseline for max comparisons for intervals
        # This is critical to ensure hypothermia only prolongs if its effect is greater than existing conditions.
        current_qt_from_state = physiological_state.get('qt_duration_ms', 440) 
        current_pr_from_state = physiological_state.get('pr_interval_ms', 160)
        current_qrs_from_state = physiological_state.get('qrs_duration_ms', 100)


        if temp_c < 35.0:  # Mild Hypothermia
            target_heart_rate = min(target_heart_rate, 60)
            target_osborn_wave_present = True
            target_pr_interval_ms = max(current_pr_from_state, 220)
            target_qrs_duration_ms = max(current_qrs_from_state, 110)
            target_qt_duration_ms = max(current_qt_from_state, 480)
        if temp_c < 32.0:  # Moderate Hypothermia (effects are cumulative/overriding)
            target_heart_rate = min(target_heart_rate, 50)
            target_osborn_wave_present = True # Remains true
            target_pr_interval_ms = max(current_pr_from_state, 240)
            target_qrs_duration_ms = max(current_qrs_from_state, 120)
            target_qt_duration_ms = max(current_qt_from_state, 500)
        if temp_c < 28.0:  # Severe Hypothermia (effects are cumulative/overriding)
            target_heart_rate = min(target_heart_rate, 40)
            target_osborn_wave_present = True # Remains true
            target_pr_interval_ms = max(current_pr_from_state, 280)
            target_qrs_duration_ms = max(current_qrs_from_state, 140)
            target_qt_duration_ms = max(current_qt_from_state, 550)

        # Drug Effects Logic
        ketamine_effect_hr_increase = 20
        morphine_effect_hr_decrease = 15

        if physiological_state.get('ketamine_active', False):
            target_heart_rate += ketamine_effect_hr_increase
        
        if physiological_state.get('morphine_active', False):
            target_heart_rate -= morphine_effect_hr_decrease
        
        # Clamping Heart Rate after all effects are applied
        target_heart_rate = max(30, min(target_heart_rate, 250))


        return {
            'target_heart_rate': target_heart_rate,
            'target_st_depression_mv': target_st_depression_mv,
            'target_qrs_amplitude_factor': target_qrs_amplitude_factor,
            'target_t_wave_amplitude_factor': target_t_wave_amplitude_factor,
            'target_qt_duration_ms': target_qt_duration_ms,
            'target_st_elevation_mv': target_st_elevation_mv,
            'target_pr_interval_ms': target_pr_interval_ms, 
            'target_qrs_duration_ms': target_qrs_duration_ms, 
            'target_osborn_wave_present': target_osborn_wave_present
        }

```
