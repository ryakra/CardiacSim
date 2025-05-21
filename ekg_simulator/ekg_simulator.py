import time
import numpy as np
from .waveform_generator import WaveformGenerator
from .dynamic_plotter import DynamicPlotter
from .physiological_effects_manager import PhysiologicalEffectsManager

class EKGSimulator:
    def __init__(self):
        self.sampling_rate = 100  # Default sampling rate
        self.waveform_generator = WaveformGenerator()
        self.plotter = DynamicPlotter(self) 
        self.current_ekg_data = np.array([])
        # How often new EKG data is generated (e.g., every 0.1 seconds)
        self.simulation_time_step_seconds = 0.1 
        # Max duration of EKG data to keep in current_ekg_data (e.g. plotter's display window + 1 second)
        self.max_buffer_duration_seconds = 11 
        self.physiological_state = {
            'blood_volume_percent': 100, 
            'heart_rate_bpm': 70, 
            'st_depression_mv': 0.0,
            'tension_pneumothorax_present': False,
            'qrs_amplitude_factor': 1.0,
            'tbi_present': False,
            'icp_mmhg': 10,
            't_wave_amplitude_factor': 1.0,
            'qt_duration_ms': 440,
            'blast_injury_present': False,
            'coronary_age_suspected': False,
            'st_elevation_mv': 0.0,
            'serum_k_meq_l': 4.0,
            'pr_interval_ms': 160,
            'qrs_duration_ms': 100,
            'serum_ca_mg_dl': 9.5,
            'core_body_temperature_celsius': 37.0,
            'osborn_wave_present': False,
            'ketamine_active': False,
            'morphine_active': False
        }
        self.effects_manager = PhysiologicalEffectsManager()
        self.total_simulation_time_seconds = 0.0

    def initialize_simulation(self, num_leads_display=1, display_seconds=10):
        """
        Initializes the simulation environment.
        Sets up the plotter and potentially pre-generates initial EKG data.
        """
        self.plotter.display_seconds = display_seconds
        self.plotter.setup_plot(num_leads=num_leads_display, sampling_rate=self.sampling_rate)
        
        # Update max_buffer_duration_seconds based on display_seconds
        self.max_buffer_duration_seconds = display_seconds + 1 

        # Pre-generate some data to fill the display window initially
        initial_duration = self.plotter.display_seconds
        if initial_duration > 0:
            print(f"Pre-generating initial EKG data for {initial_duration} seconds...")
            initial_data = self.waveform_generator.get_ekg_segment(
                duration_seconds=initial_duration,
                sampling_rate=self.sampling_rate,
                heart_rate=self.physiological_state['heart_rate_bpm'],
                st_depression_mv=self.physiological_state['st_depression_mv']
            )
            self.current_ekg_data = initial_data
            print(f"Initial data generated, shape: {self.current_ekg_data.shape}")
        else:
            print("Warning: display_seconds is 0, no initial data will be plotted.")


    def _generate_new_data_segment(self):
        """
        Generates a new chunk of EKG data and appends it to the internal buffer.
        This method is called by get_latest_ekg_data before returning data to the plotter.
        """
        # Simulate gradual blood loss for testing
        if self.physiological_state['blood_volume_percent'] > 40: # Stop at a severe level
            self.physiological_state['blood_volume_percent'] -= 0.05 # Small decrement per data generation cycle
        
        # Update total simulation time
        self.total_simulation_time_seconds += self.simulation_time_step_seconds

        # Test logic for applying tension pneumothorax after a delay
        if self.total_simulation_time_seconds > 15 and not self.physiological_state['tension_pneumothorax_present'] and not self.physiological_state['tbi_present']: # Avoid overlap for testing clarity
            print("SIMULATOR: Applying Tension Pneumothorax") # For console feedback
            self.set_tension_pneumothorax(True)
        
        # Test Logic for TBI (similar to Tension Pneumo)
        if self.total_simulation_time_seconds > 30 and not self.physiological_state['tbi_present'] and \
           not self.physiological_state['tension_pneumothorax_present'] and not self.physiological_state['blast_injury_present']: # Apply after 30s, avoid overlaps
            print("SIMULATOR: Applying TBI with Raised ICP") # For console feedback
            self.set_tbi(True, icp=30) # Example ICP value

        # Test Logic for Blast Injury
        if self.total_simulation_time_seconds > 45 and \
           not self.physiological_state['blast_injury_present'] and \
           not self.physiological_state['tbi_present'] and \
           not self.physiological_state['tension_pneumothorax_present']:
            print("SIMULATOR: Applying Blast Injury with suspected Coronary AGE")
            self.set_blast_injury(True, suspect_age=True)

        # Test Logic for Hyperkalemia
        # Apply after 60s, ensure no other major condition is active for clarity
        if self.total_simulation_time_seconds > 60 and \
           self.physiological_state['serum_k_meq_l'] < 5.0 and \
           not self.physiological_state['blast_injury_present'] and \
           not self.physiological_state['tbi_present'] and \
           not self.physiological_state['tension_pneumothorax_present']:
            print("SIMULATOR: Inducing Moderate Hyperkalemia (K+ = 6.8)")
            self.set_serum_potassium(6.8)
        elif self.total_simulation_time_seconds > 75 and \
             self.physiological_state['serum_k_meq_l'] < 7.5 and \
             not self.physiological_state['blast_injury_present'] and \
             not self.physiological_state['tbi_present'] and \
             not self.physiological_state['tension_pneumothorax_present']:
            print("SIMULATOR: Inducing Severe Hyperkalemia (K+ = 8.0)")
            self.set_serum_potassium(8.0)

        # Test Logic for Hypocalcemia
        # Apply after 90s, ensure no other major condition is active for clarity
        if self.total_simulation_time_seconds > 90 and \
           self.physiological_state['serum_ca_mg_dl'] > 8.0 and \
           not self.physiological_state['blast_injury_present'] and \
           not self.physiological_state['tbi_present'] and \
           not self.physiological_state['tension_pneumothorax_present'] and \
           self.physiological_state['serum_k_meq_l'] < 5.0 : # Avoid compounding electrolyte issues for test clarity
            print("SIMULATOR: Inducing Mild Hypocalcemia (Ca = 8.0 mg/dL)")
            self.set_serum_calcium(8.0)
        elif self.total_simulation_time_seconds > 105 and \
             self.physiological_state['serum_ca_mg_dl'] > 6.5 and \
             not self.physiological_state['blast_injury_present'] and \
             not self.physiological_state['tbi_present'] and \
             not self.physiological_state['tension_pneumothorax_present'] and \
             self.physiological_state['serum_k_meq_l'] < 5.0 :
            print("SIMULATOR: Inducing Severe Hypocalcemia (Ca = 6.5 mg/dL)")
            self.set_serum_calcium(6.5)

        # Test Logic for Hypothermia
        # Apply after 120s, ensure no other major conditions are active for clarity
        if self.total_simulation_time_seconds > 120 and \
           self.physiological_state['core_body_temperature_celsius'] > 34.0 and \
           not self.physiological_state['blast_injury_present'] and \
           not self.physiological_state['tbi_present'] and \
           not self.physiological_state['tension_pneumothorax_present'] and \
           self.physiological_state['serum_k_meq_l'] < 5.0 and \
           self.physiological_state['serum_ca_mg_dl'] > 8.5:
            print("SIMULATOR: Inducing Mild Hypothermia (Temp = 34.0 C)")
            self.set_core_body_temperature(34.0)
        elif self.total_simulation_time_seconds > 135 and \
             self.physiological_state['core_body_temperature_celsius'] > 31.0 and \
             not self.physiological_state['blast_injury_present'] and \
             not self.physiological_state['tbi_present'] and \
             not self.physiological_state['tension_pneumothorax_present'] and \
             self.physiological_state['serum_k_meq_l'] < 5.0 and \
             self.physiological_state['serum_ca_mg_dl'] > 8.5:
            print("SIMULATOR: Inducing Moderate Hypothermia (Temp = 31.0 C)")
            self.set_core_body_temperature(31.0)

        # Test Ketamine after 150s
        if self.total_simulation_time_seconds > 150 and \
           not self.physiological_state['ketamine_active'] and \
           not self.physiological_state['morphine_active'] and \
           not self.physiological_state['blast_injury_present'] and \
           not self.physiological_state['tbi_present'] and \
           not self.physiological_state['tension_pneumothorax_present']: 
            print("SIMULATOR: Administering Ketamine")
            self.administer_ketamine(True)

        # Test Morphine after 165s (after Ketamine effect might have been visible or if Ketamine wasn't given)
        # To make it clearer, let's reset Ketamine before Morphine for testing
        if self.total_simulation_time_seconds > 165 and self.physiological_state['ketamine_active']:
            print("SIMULATOR: Clearing Ketamine before Morphine test")
            self.administer_ketamine(False) # Clear ketamine

        if self.total_simulation_time_seconds > 170 and \
           not self.physiological_state['morphine_active'] and \
           not self.physiological_state['ketamine_active'] and \
           not self.physiological_state['blast_injury_present'] and \
           not self.physiological_state['tbi_present'] and \
           not self.physiological_state['tension_pneumothorax_present']:
            print("SIMULATOR: Administering Morphine")
            self.administer_morphine(True)


        target_ekg_params = self.effects_manager.update_ekg_parameters(self.physiological_state)
        self.physiological_state['heart_rate_bpm'] = target_ekg_params['target_heart_rate']
        self.physiological_state['st_depression_mv'] = target_ekg_params['target_st_depression_mv']
        self.physiological_state['st_elevation_mv'] = target_ekg_params['target_st_elevation_mv']
        self.physiological_state['qrs_amplitude_factor'] = target_ekg_params['target_qrs_amplitude_factor']
        self.physiological_state['t_wave_amplitude_factor'] = target_ekg_params['target_t_wave_amplitude_factor']
        self.physiological_state['qt_duration_ms'] = target_ekg_params['target_qt_duration_ms']
        self.physiological_state['pr_interval_ms'] = target_ekg_params['target_pr_interval_ms']
        self.physiological_state['qrs_duration_ms'] = target_ekg_params['target_qrs_duration_ms']
        self.physiological_state['osborn_wave_present'] = target_ekg_params['target_osborn_wave_present']

        
        # print(f"Generating new EKG data segment for {self.simulation_time_step_seconds} seconds...")
        new_segment = self.waveform_generator.get_ekg_segment(
            duration_seconds=self.simulation_time_step_seconds,
            sampling_rate=self.sampling_rate,
            heart_rate=self.physiological_state['heart_rate_bpm'],
            st_depression_mv=self.physiological_state['st_depression_mv'],
            st_elevation_mv=self.physiological_state['st_elevation_mv'],
            qrs_amplitude_factor=self.physiological_state['qrs_amplitude_factor'],
            t_wave_amplitude_factor=self.physiological_state['t_wave_amplitude_factor'],
            target_qt_duration_ms=self.physiological_state['qt_duration_ms'],
            target_pr_interval_ms=self.physiological_state['pr_interval_ms'],
            target_qrs_duration_ms=self.physiological_state['qrs_duration_ms'],
            osborn_wave_present=self.physiological_state['osborn_wave_present']
        )
        
        # Append new segment
        self.current_ekg_data = np.concatenate((self.current_ekg_data, new_segment))

        # Trim current_ekg_data to keep it from growing indefinitely
        # It should hold a bit more than what DynamicPlotter displays
        max_buffer_points = int(self.max_buffer_duration_seconds * self.sampling_rate)
        if len(self.current_ekg_data) > max_buffer_points:
            self.current_ekg_data = self.current_ekg_data[-max_buffer_points:]
        # print(f"New data segment generated. Buffer size: {len(self.current_ekg_data)} points.")

    def get_latest_ekg_data(self):
        """
        Called by DynamicPlotter to get data for plotting.
        This method ensures that new data is generated before being passed to the plotter.
        """
        self._generate_new_data_segment()
        
        # Return the portion of data that should be displayed by the plotter
        # This corresponds to the most recent 'display_seconds' worth of data.
        num_points_to_display = int(self.plotter.display_seconds * self.sampling_rate)
        
        if len(self.current_ekg_data) < num_points_to_display:
            # If buffer is not full yet, return all of it
            # print(f"Returning {len(self.current_ekg_data)} points (buffer not full).")
            return self.current_ekg_data
        else:
            # Return the last 'num_points_to_display' data points
            # print(f"Returning last {num_points_to_display} points from buffer.")
            return self.current_ekg_data[-num_points_to_display:]

    def run_simulation(self):
        """
        Starts the EKG simulation and plotting.
        """
        print("Initializing simulation...")
        # Default display_seconds for plotter can be set here if not already
        self.initialize_simulation(display_seconds=self.plotter.display_seconds) 
        
        print("Starting animation...")
        self.plotter.start_animation()
        print("Simulation finished or plot window closed.")

    def set_blood_volume_percentage(self, percentage):
        """
        Sets the blood volume percentage for the physiological state.
        Ensures the percentage is clamped between 0 and 100.
        """
        self.physiological_state['blood_volume_percent'] = np.clip(percentage, 0, 100)
        print(f"Blood volume percentage set to: {self.physiological_state['blood_volume_percent']}%")

    def set_tension_pneumothorax(self, present: bool):
        """
        Sets the tension pneumothorax state.
        """
        self.physiological_state['tension_pneumothorax_present'] = present
        print(f"Tension pneumothorax state set to: {present}")

    def set_tbi(self, present: bool, icp: int = 10):
        """
        Sets the TBI state and ICP level.
        """
        self.physiological_state['tbi_present'] = present
        self.physiological_state['icp_mmhg'] = icp
        print(f"TBI state set to: {present}, ICP set to: {icp} mmHg")

    def set_blast_injury(self, present: bool, suspect_age: bool = False):
        """
        Sets the blast injury state and whether coronary AGE is suspected.
        """
        self.physiological_state['blast_injury_present'] = present
        self.physiological_state['coronary_age_suspected'] = suspect_age
        print(f"Blast injury state set to: {present}, Coronary AGE suspected: {suspect_age}")

    def set_serum_potassium(self, k_level: float):
        """
        Sets the serum potassium level.
        """
        self.physiological_state['serum_k_meq_l'] = k_level
        print(f"Serum K+ level set to: {k_level} mEq/L")

    def set_serum_calcium(self, ca_level: float):
        """
        Sets the serum calcium level.
        """
        self.physiological_state['serum_ca_mg_dl'] = ca_level
        print(f"Serum Ca level set to: {ca_level} mg/dL")

    def set_core_body_temperature(self, temp_celsius: float):
        """
        Sets the core body temperature.
        """
        self.physiological_state['core_body_temperature_celsius'] = temp_celsius
        print(f"Core body temperature set to: {temp_celsius}°C")

    def administer_ketamine(self, active: bool):
        """
        Sets the ketamine administration state.
        """
        self.physiological_state['ketamine_active'] = active
        print(f"Ketamine active state set to: {active}")

    def administer_morphine(self, active: bool):
        """
        Sets the morphine administration state.
        """
        self.physiological_state['morphine_active'] = active
        print(f"Morphine active state set to: {active}")
```
