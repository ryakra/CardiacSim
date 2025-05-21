import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class DynamicPlotter:
    def __init__(self, ekg_simulator_instance):
        self.ekg_simulator_instance = ekg_simulator_instance
        self.fig = None
        self.ax = None
        self.line = None
        self.data_buffer = []
        self.display_seconds = 10  # Default display duration
        self.sampling_rate = 100 # Default sampling rate
        self.hr_annotation = None
        self.st_annotation = None # This will handle both depression and elevation text
        self.pneumo_annotation = None
        self.tbi_annotation = None
        self.blast_annotation = None
        self.k_annotation = None
        self.ca_annotation = None
        self.temp_annotation = None
        self.osborn_annotation = None
        self.ket_annotation = None
        self.morph_annotation = None
        # self.ste_annotation = None # Removed as per refined instructions to use one st_annotation

    def setup_plot(self, num_leads=1, sampling_rate=100):
        self.sampling_rate = sampling_rate
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")
        self.ax.set_title("Real-time EKG Signal")
        self.line, = self.ax.plot([], [], lw=2) # lw is line width
        self.ax.set_xlim(0, self.display_seconds)
        self.ax.set_ylim(-2.0, 2.0) # Adjusted y_lim for potential scaled QRS

        # Add text annotations for HR and ST depression/elevation
        self.hr_annotation = self.ax.text(0.02, 0.95, '', transform=self.ax.transAxes, fontsize=10,
                                          verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', fc='wheat', alpha=0.5))
        # ST annotation will now be used for depression or elevation
        self.st_annotation = self.ax.text(0.02, 0.85, '', transform=self.ax.transAxes, fontsize=10, 
                                           verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', fc='wheat', alpha=0.5))
        self.pneumo_annotation = self.ax.text(0.02, 0.75, '', transform=self.ax.transAxes, fontsize=10, color='red',
                                              verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', fc='lightcoral', alpha=0.7))
        self.tbi_annotation = self.ax.text(0.02, 0.65, '', transform=self.ax.transAxes, fontsize=10, color='orange', 
                                             verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', fc='moccasin', alpha=0.7))
        self.blast_annotation = self.ax.text(0.02, 0.55, '', transform=self.ax.transAxes, fontsize=10, color='magenta', 
                                             verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', fc='plum', alpha=0.7))
        self.k_annotation = self.ax.text(0.02, 0.45, '', transform=self.ax.transAxes, fontsize=10, color='blue', 
                                          verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', fc='lightblue', alpha=0.7))
        self.ca_annotation = self.ax.text(0.02, 0.35, '', transform=self.ax.transAxes, fontsize=10, color='green', 
                                           verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', fc='lightgreen', alpha=0.7))
        self.temp_annotation = self.ax.text(0.02, 0.25, '', transform=self.ax.transAxes, fontsize=10, color='cyan', # Adjusted y position
                                            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', fc='lightcyan', alpha=0.7))
        self.osborn_annotation = self.ax.text(0.02, 0.15, '', transform=self.ax.transAxes, fontsize=10, color='teal', 
                                              verticalalignment='top', bbox=dict(boxstyle='round,pad=0.3', fc='paleturquoise', alpha=0.7))
        
        # Drug annotations on the right side
        self.ket_annotation = self.ax.text(0.98, 0.95, '', transform=self.ax.transAxes, fontsize=10, color='purple', 
                                           verticalalignment='top', horizontalalignment='right',
                                           bbox=dict(boxstyle='round,pad=0.3', fc='violet', alpha=0.5))
        self.morph_annotation = self.ax.text(0.98, 0.85, '', transform=self.ax.transAxes, fontsize=10, color='indigo',  # Adjusted y position
                                             verticalalignment='top', horizontalalignment='right',
                                             bbox=dict(boxstyle='round,pad=0.3', fc='thistle', alpha=0.5))


        # Placeholder for multi-lead, not implemented in this phase
        if num_leads > 1:
            print("Warning: Multi-lead display is not fully implemented in this version.")

    def _update_plot(self, frame):
        # Get data from the EKG simulator instance
        # This method in EKGSimulator should provide the latest data segment
        new_data_segment = self.ekg_simulator_instance.get_latest_ekg_data()

        if new_data_segment is not None and len(new_data_segment) > 0:
            # Append new data to our buffer
            self.data_buffer.extend(new_data_segment)

            # Trim buffer to display_seconds
            max_points = int(self.display_seconds * self.sampling_rate)
            if len(self.data_buffer) > max_points:
                self.data_buffer = self.data_buffer[-max_points:]

            # Create time vector for plotting
            time_vector = np.linspace(0, self.display_seconds, len(self.data_buffer), endpoint=False)
            
            self.line.set_data(time_vector, self.data_buffer)
            
            # Adjust x-axis if necessary (though for scrolling, it's often fixed)
            # self.ax.set_xlim(time_vector.min(), time_vector.max()) 
            # For a fixed scrolling window, xlim is already set in setup_plot
        
        # Fetch current physiological parameters
        current_hr = self.ekg_simulator_instance.physiological_state.get('heart_rate_bpm', 0)
        current_st = self.ekg_simulator_instance.physiological_state.get('st_depression_mv', 0.0)
        tension_pneumothorax_present = self.ekg_simulator_instance.physiological_state.get('tension_pneumothorax_present', False)
        current_qrs_amplitude_factor = self.ekg_simulator_instance.physiological_state.get('qrs_amplitude_factor', 1.0)
        tbi_present = self.ekg_simulator_instance.physiological_state.get('tbi_present', False)
        icp_mmhg = self.ekg_simulator_instance.physiological_state.get('icp_mmhg', 10)
        blast_injury_present = self.ekg_simulator_instance.physiological_state.get('blast_injury_present', False)
        st_elevation_mv = self.ekg_simulator_instance.physiological_state.get('st_elevation_mv', 0.0)
        st_depression_mv = current_st 
        serum_k_meq_l = self.ekg_simulator_instance.physiological_state.get('serum_k_meq_l', 4.0)
        serum_ca_mg_dl = self.ekg_simulator_instance.physiological_state.get('serum_ca_mg_dl', 9.5)
        temp_c = self.ekg_simulator_instance.physiological_state.get('core_body_temperature_celsius', 37.0)
        osborn_expected = self.ekg_simulator_instance.physiological_state.get('osborn_wave_present', False)
        ket_active = self.ekg_simulator_instance.physiological_state.get('ketamine_active', False)
        morph_active = self.ekg_simulator_instance.physiological_state.get('morphine_active', False)


        # Update annotations
        self.hr_annotation.set_text(f'HR: {current_hr:.0f} bpm')
        
        st_text = ''
        if st_elevation_mv > 0:
            st_text = f'ST Elev: {st_elevation_mv:.2f} mV (AGE?)'
            self.st_annotation.set_bbox(dict(boxstyle='round,pad=0.3', fc='lightcoral', alpha=0.7)) 
        elif st_depression_mv > 0:
            st_text = f'ST Dep: {st_depression_mv:.2f} mV'
            self.st_annotation.set_bbox(dict(boxstyle='round,pad=0.3', fc='wheat', alpha=0.5)) 
        else:
            self.st_annotation.set_bbox(dict(boxstyle='round,pad=0.3', fc='wheat', alpha=0.5)) 
        self.st_annotation.set_text(st_text)
        
        self.pneumo_annotation.set_text('Tension Pneumo' if tension_pneumothorax_present else '')
        self.tbi_annotation.set_text(f'TBI | ICP: {icp_mmhg} mmHg' if tbi_present else '')
        self.blast_annotation.set_text('Blast Injury' if blast_injury_present else '')

        k_text = f'K+: {serum_k_meq_l:.1f} mEq/L'
        if serum_k_meq_l > 5.5:
            self.k_annotation.set_text(k_text + ' (High)')
            self.k_annotation.set_color('red')
            self.k_annotation.set_bbox(dict(boxstyle='round,pad=0.3', fc='salmon', alpha=0.7))
        else:
            self.k_annotation.set_text(k_text)
            self.k_annotation.set_color('blue')
            self.k_annotation.set_bbox(dict(boxstyle='round,pad=0.3', fc='lightblue', alpha=0.7))
        
        ca_text = f'Ca: {serum_ca_mg_dl:.1f} mg/dL'
        if serum_ca_mg_dl < 8.5:
            self.ca_annotation.set_text(ca_text + ' (Low)')
            self.ca_annotation.set_color('red') 
            self.ca_annotation.set_bbox(dict(boxstyle='round,pad=0.3', fc='lightcoral', alpha=0.7))
        else:
            self.ca_annotation.set_text(ca_text)
            self.ca_annotation.set_color('green')
            self.ca_annotation.set_bbox(dict(boxstyle='round,pad=0.3', fc='lightgreen', alpha=0.7))

        temp_text = f'Temp: {temp_c:.1f}°C'
        if temp_c < 35.0:
            self.temp_annotation.set_text(temp_text + ' (Low)')
            self.temp_annotation.set_color('red')
            self.temp_annotation.set_bbox(dict(boxstyle='round,pad=0.3', fc='salmon', alpha=0.7))
        else:
            self.temp_annotation.set_text(temp_text)
            self.temp_annotation.set_color('cyan')
            self.temp_annotation.set_bbox(dict(boxstyle='round,pad=0.3', fc='lightcyan', alpha=0.7))
            
        self.osborn_annotation.set_text('Osborn Waves Expected' if osborn_expected else '')

        self.ket_annotation.set_text('Ketamine Active' if ket_active else '')
        self.morph_annotation.set_text('Morphine Active' if morph_active else '')

        
        # Adjust Y-axis limits dynamically based on QRS amplitude factor, if needed
        # This is a simple way to try and keep the scaled waveform visible.
        # Could also adjust based on actual data min/max if preferred.
        if current_qrs_amplitude_factor < 0.7: # Example threshold
            self.ax.set_ylim(-1.0 * current_qrs_amplitude_factor * 2, 1.0 * current_qrs_amplitude_factor * 2)
        elif self.ax.get_ylim()[1] < 1.5 : # Reset if it was shrunk and factor is back to normal
             self.ax.set_ylim(-1.5, 1.5)


        return self.line, self.hr_annotation, self.st_annotation, self.pneumo_annotation, self.tbi_annotation, self.blast_annotation, self.k_annotation, self.ca_annotation, self.temp_annotation, self.osborn_annotation, self.ket_annotation, self.morph_annotation

    def start_animation(self):
        if self.fig is None:
            print("Error: Plot not set up. Call setup_plot() first.")
            return

        # The interval should ideally be linked to data generation frequency
        # For example, if EKGSimulator generates data every 100ms (0.1s),
        # interval could be 100ms.
        # FuncAnimation will call _update_plot roughly every 'interval' milliseconds.
        animation_interval = self.ekg_simulator_instance.simulation_time_step_seconds * 1000
        
        ani = FuncAnimation(self.fig, self._update_plot, blit=True, 
                            interval=animation_interval, save_count=50)
        try:
            plt.show()
        except Exception as e:
            print(f"Error displaying plot: {e}")
            print("Ensure you have a GUI backend for Matplotlib, e.g., qt5agg.")
            print("You might need to run 'sudo apt-get install python3-tk' or similar for your OS.")
